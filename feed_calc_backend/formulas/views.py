import csv
import io
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .models import Formula, FormulaItem
from .serializers import FormulaSerializer
from .services import FormulaService
from ingredients.models import Ingredient


def _parse_formula_csv(content_bytes):
    """
    Parse the CSV format produced by FormulaExporter.vue downloadCSV().
    Returns (meta dict, items list of (name, amount_kg)).
    """
    text = content_bytes.decode('utf-8-sig')  # strip UTF-8 BOM if present
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)

    META_KEYS = {
        '配方名稱': 'name',
        '客戶名稱': 'customer_name',
        '物種/階段': 'species_stage',
        '參考標準': 'standard_name',
        '日期': 'date',
        '備註': 'description',
    }

    meta = {}
    items = []
    in_composition = False

    for row in rows:
        stripped = [c.strip() for c in row]
        if not any(stripped):
            in_composition = False
            continue

        first = stripped[0]

        if first in META_KEYS and len(stripped) >= 2:
            meta[META_KEYS[first]] = stripped[1]
            continue

        if first == '原料名稱' and len(stripped) >= 2 and '使用量' in stripped[1]:
            in_composition = True
            continue

        if first == '營養項目':
            in_composition = False
            continue

        if in_composition and len(stripped) >= 2 and first:
            try:
                amount = float(stripped[1])
                items.append((first, amount))
            except ValueError:
                pass

    return meta, items

# 自訂權限：允許所有人讀取，但只有作者能修改/刪除
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # 如果是 GET, HEAD, OPTIONS (讀取類)，直接放行
        if request.method in permissions.SAFE_METHODS:
            return True
        # 如果是 PUT, DELETE (修改類)，檢查是否為作者
        return obj.created_by == request.user

class FormulaListView(generics.ListCreateAPIView):
    serializer_class = FormulaSerializer
    # 列表頁：只要登入就能看，也能新增
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # ✨ [關鍵修改] 回傳「所有」配方，而不只是自己的
        # 這樣你就能看到並載入其他人 (或你自己以前) 建立的配方
        return Formula.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        # 新增時，自動填入當前登入者
        serializer.save(created_by=self.request.user)

class FormulaDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FormulaSerializer
    # 詳細頁：登入可讀，但只有作者可改 (IsOwnerOrReadOnly)
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        # ✨ [關鍵修改] 允許查詢所有配方，否則點擊非自己的配方會 404
        return Formula.objects.all()


class FormulaImportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        csv_file = request.FILES.get('file')
        if not csv_file:
            return Response({'error': '未提供 CSV 檔案'}, status=400)

        try:
            meta, raw_items = _parse_formula_csv(csv_file.read())
        except Exception as e:
            return Response({'error': f'CSV 解析失敗: {str(e)}'}, status=400)

        if not raw_items:
            return Response({'error': 'CSV 中未找到原料資料'}, status=400)

        user = request.user
        accessible_qs = Ingredient.objects.filter(Q(is_public=True) | Q(created_by=user))

        matched = []
        unmatched = []
        for name, amount_kg in raw_items:
            ing = (
                accessible_qs.filter(name=name).first() or
                accessible_qs.filter(name__iexact=name).first() or
                accessible_qs.filter(name__icontains=name).first()
            )
            if ing:
                matched.append((ing.id, amount_kg))
            else:
                unmatched.append(name)

        if not matched:
            return Response(
                {'error': '所有原料皆無法比對，請確認 CSV 格式與資料庫一致', 'unmatched': unmatched},
                status=400,
            )

        formula = Formula.objects.create(
            name=meta.get('name', '匯入配方'),
            description=meta.get('description', ''),
            created_by=user,
        )
        for ing_id, amount_kg in matched:
            FormulaItem.objects.create(
                formula=formula,
                ingredient_id=ing_id,
                amount_kg=amount_kg,
            )
        FormulaService.calculate_and_save(formula)

        serializer = FormulaSerializer(formula, context={'request': request})
        return Response({'formula': serializer.data, 'unmatched': unmatched}, status=201)
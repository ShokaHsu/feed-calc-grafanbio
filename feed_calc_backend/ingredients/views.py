from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .models import Ingredient
from .serializers import IngredientSerializer


class IngredientListView(generics.ListCreateAPIView):
    """
    GET: 取得原料列表 (包含系統公用 + 個人自訂)
    POST: 新增自訂原料 (受會員等級限制)
    """
    serializer_class = IngredientSerializer
    # 允許未登入者讀取 (看公用資料)，但只有登入者能新增
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        
        # 1. 基礎查詢：所有人都能看到「系統公用 (is_public=True)」的原料
        # feed_database.xlsx 匯入後的資料,不管有沒有登入，皆能看到
        public_query = Q(is_public=True)

        if user.is_authenticated:
            # 2. 登入者：可以看到「系統公用」 OR 「自己建立 (created_by=user)」
            my_query = Q(created_by=user)
            
            # 3. 企業會員邏輯 (若有組織，且同事有分享)
            org_query = Q()
            if hasattr(user, 'tier') and user.tier == 'ENTERPRISE' and user.organization:
                org_query = Q(
                    created_by__organization=user.organization, 
                    share_with_org=True
                )
            
            # 組合所有條件 (使用 | 代表 OR)
            qs = Ingredient.objects.filter(public_query | my_query | org_query)
        else:
            # 未登入：只看公用
            qs = Ingredient.objects.filter(public_query)

        
        # --- 篩選器處理 ---

        # 4. 支援關鍵字搜尋 (?q=玉米)
        q = self.request.query_params.get("q", "").strip()
        if q:
            qs = qs.filter(name__icontains=q)
            
        # 5. 支援分類篩選 (?category=CEREAL)
        # 前端傳來的 category 參數，如果不是空字串，就進行篩選
        category = self.request.query_params.get("category", "").strip()
        if category:
            qs = qs.filter(category=category)

        # 去除重複並排序
        return qs.distinct().order_by("name")

    def perform_create(self, serializer):
        # 新增時，強制設定為私有，並歸戶給當前使用者
        serializer.save(created_by=self.request.user, is_public=False)

class IngredientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # 詳細頁面也套用相同的過濾邏輯，避免偷看別人的資料
        user = self.request.user
        base_query = Q(is_public=True)
        
        if user.is_authenticated:
            my_query = Q(created_by=user)
            return Ingredient.objects.filter(base_query | my_query)
        
        return Ingredient.objects.filter(base_query)

# ✨ [新增] 批次刪除 API
class IngredientBulkDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # 預期接收格式: { "ids": [1, 5, 8] }
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'detail': '未提供 ID 列表'}, status=status.HTTP_400_BAD_REQUEST)

        # 執行刪除 (加上權限過濾，只能刪除自己建立的)
        # 系統公用原料 (is_public=True) 即使傳了 ID 也不會被刪除，除非你是 Superuser
        qs = Ingredient.objects.filter(id__in=ids)
        
        if not request.user.is_superuser:
            # 一般使用者只能刪除自己建立的
            qs = qs.filter(created_by=request.user)

        deleted_count, _ = qs.delete()
        
        return Response({'detail': f'成功刪除 {deleted_count} 筆原料'}, status=status.HTTP_200_OK)
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .models import NutrientStandard
from .serializers import NutrientStandardSerializer
from .models import NutrientStandard

class StandardListView(generics.ListCreateAPIView):
    """
    GET: 取得標準列表 (公用 + 私有)
    POST: 建立新標準 (自動設為私有)
    """
    serializer_class = NutrientStandardSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = NutrientStandard.objects.all()
        q = self.request.query_params.get('q', None)
        if q:
            queryset = queryset.filter(name__icontains=q)
        if user.is_authenticated:
            return queryset.filter(Q(is_public=True) | Q(created_by=user))
        return queryset.filter(is_public=True)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, is_public=False)


class StandardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/DELETE 單一標準 — 僅限擁有者可修改/刪除
    """
    serializer_class = NutrientStandardSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return NutrientStandard.objects.filter(Q(is_public=True) | Q(created_by=user))
        return NutrientStandard.objects.filter(is_public=True)

# ✨輔助 View：用於回傳所有已定義的生長階段列表
class StageListView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # 允許登入或唯讀存取

    def get(self, request, *args, **kwargs):
        # 獲取所有獨特的 stage 代碼
        # .values() 獲取字典，.distinct() 去重
        stages = NutrientStandard.objects.values('species', 'stage').distinct()
        
        # 建立中文對照表 (從 NutrientStandard Model 獲取)
        stage_choices = dict(NutrientStandard.STAGE_CHOICES)
        species_choices = dict(NutrientStandard.SPECIES_CHOICES)
        
        # 格式化輸出
        data = [
            {
                'species': s['species'],
                'species_zh': species_choices.get(s['species'], s['species']),
                'stage_code': s['stage'],
                'stage_zh': stage_choices.get(s['stage'], s['stage']),
            } 
            for s in stages
        ]
        
        return Response(data)
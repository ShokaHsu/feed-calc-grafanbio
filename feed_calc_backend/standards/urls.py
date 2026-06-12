from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import StandardListView, StandardDetailView, StageListView

app_name = "standards"

urlpatterns = [
   # 營養規格列表
    path('requirements/', StandardListView.as_view(), name='standard-list'),
    path('requirements/<int:pk>/', StandardDetailView.as_view(), name='standard-detail'),
    
    # ✨ [新增] 輔助 API：取得所有生長階段列表
    path('stages/', StageListView.as_view(), name='stage-list'),
    
    # 單筆詳細資料 API
    path('<int:pk>/', StandardDetailView.as_view(), name='standard-detail'),
]
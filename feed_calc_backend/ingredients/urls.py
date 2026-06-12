# ingredients/urls.py
from django.urls import path
from .views import IngredientListView, IngredientDetailView, IngredientBulkDeleteView

app_name = "ingredients"

urlpatterns = [
    # 對應到 /api/ingredients/ (由主 urls 決定前綴)
    path("", IngredientListView.as_view(), name="list"),
    
    # 對應到 /api/ingredients/<pk>/
    path("<int:pk>/", IngredientDetailView.as_view(), name="detail"),

    # ✨ [新增] 批次刪除路由
    path('bulk-delete/', IngredientBulkDeleteView.as_view(), name='ingredient-bulk-delete'),
]
from django.urls import path
from .views import FormulaListView, FormulaDetailView, FormulaImportView

app_name = 'formulas'

urlpatterns = [
    # API 路徑: /api/formulas/
    # GET: 取得我的配方列表
    # POST: 建立新配方 (包含原料明細)
    path('', FormulaListView.as_view(), name='formula-list'),

    # API 路徑: /api/formulas/<pk>/
    # GET: 取得特定配方詳情
    # PUT/PATCH: 修改配方 (包含原料明細)
    # DELETE: 刪除配方
    path('<int:pk>/', FormulaDetailView.as_view(), name='formula-detail'),
    path('import-csv/', FormulaImportView.as_view(), name='formula-import-csv'),
]
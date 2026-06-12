from django.contrib import admin
from .models import Formula, FormulaItem

# 建立一個「內嵌表格」，讓原料明細可以直接顯示在配方頁面中
class FormulaItemInline(admin.TabularInline):
    model = FormulaItem
    extra = 1 # 預設顯示 1 個空白列方便新增
    autocomplete_fields = ['ingredient'] # 讓原料選單變成搜尋框 (避免下拉選單太長)

@admin.register(Formula)
class FormulaAdmin(admin.ModelAdmin):
    # 列表頁顯示的欄位
    list_display = ('name', 'customer', 'standard', 'batch_size', 'total_cost', 'cost_per_kg', 'created_by', 'created_at')
    
    # 右側篩選器
    list_filter = ('created_by', 'customer','standard__species', 'created_at')
    
    # 搜尋框 (可搜尋配方名、牧場名)
    search_fields = ('name', 'customer', 'description')
    
    # 將內嵌表格加入
    inlines = [FormulaItemInline]
    
    # 設定唯讀欄位 (成本由系統計算，不建議手動改)
    readonly_fields = ('total_cost', 'cost_per_kg', 'created_at', 'updated_at')

    # 為了讓 FormulaItemInline 的 autocomplete_fields 生效，
    # 我們必須確保 IngredientAdmin 有設定 search_fields。
    # (這在 ingredients/admin.py 應該已經設定過了)
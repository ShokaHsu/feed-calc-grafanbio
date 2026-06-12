from django.contrib import admin
from .models import Ingredient, CATEGORY_CHOICES

# ==========================================
# 批量動作產生器 (Factory Function)
# 這會自動為每一個分類產生一個 Action
# ==========================================
def make_set_category_action(category_code, category_label):
    def set_category(modeladmin, request, queryset):
        updated_count = queryset.update(category=category_code)
        modeladmin.message_user(request, f'{updated_count} 筆原料已成功更新為分類：{category_label}')
    
    # Action 在選單中的顯示名稱
    set_category.short_description = f"批量變更分類為 -> {category_label}"
    # Action 的函數名稱 (必須唯一)
    set_category.__name__ = f'set_category_{category_code}'
    return set_category



@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    # 1. 列表頁顯示 (挑選最重要的欄位即可)
    list_display = (
        'name', 
        'category', 
        'crude_protein_percent', 
        'me_pig_kcal_per_kg', 
        'amen_broiler_kcal_per_kg', # 新增肉雞 AMEn 預覽
        'cost_per_kg_twd', 
        'is_public', 
        'created_by'
    )
    
    actions = [make_set_category_action(code, label) for code, label in CATEGORY_CHOICES]

    # 2. 篩選器
    list_filter = ('category', 'is_public', 'share_with_org')
    # 在這裡加入想要直接在列表修改的欄位
    list_editable = ('category', 'cost_per_kg_twd', 'is_public')
    
    # 3. 搜尋
    search_fields = ('name', 'category')
    
    # 4. 排序
    ordering = ('category', 'name')

    # 5. 每頁顯示數量 (設大一點方便批量操作)
    list_per_page = 50

    # 6. 編輯頁面分組 (因欄位眾多，強烈建議分組)
    fieldsets = (
        ('基本資料 & 權限', {
            'fields': (
                ('name', 'category'),
                ('cost_per_kg_twd', 'created_by'),
                ('is_public', 'share_with_org')
            )
        }),
        
        ('1. 主要成分 (Proximate Analysis)', {
            'classes': ('collapse',),
            'fields': (
                ('dm_percent', 'ash_percent'),
                ('crude_protein_percent', 'crude_fat_percent', 'crude_fiber_percent'),
                ('starch_percent', 'sugar_percent'),
                ('ndf_percent', 'adf_percent'),
            )
        }),

        ('2. 碳水化合物與纖維 (Carbohydrates & Fiber)', {
            'classes': ('collapse',),
            'fields': (
                ('tdf_percent', 'nsp_percent'),
                ('sol_nsp_percent', 'insol_nsp_percent'),
            )
        }),

        ('3. 能量 (Energy)', {
            'classes': ('collapse',),
            'description': '包含豬、家禽與反芻動物的能量指標',
            'fields': (
                # 豬
                ('de_pig_kcal_per_kg', 'me_pig_kcal_per_kg'),
                ('ne_pig_growth_kcal_per_kg', 'ne_pig_sow_kcal_per_kg'),
                # 家禽
                ('amen_broiler_kcal_per_kg', 'amen_cockerel_kcal_per_kg'),
                # 反芻
                ('tdn_percent', 'me_ruminant_kcal_per_kg', 'ne_ruminant_kcal_per_kg'),
            )
        }),

        ('4. 脂肪酸 (Fatty Acids)', {
            'classes': ('collapse',),
            'fields': (
                ('linoleic_acid_g_kg', 'linolenic_acid_g_kg'),
                ('sfa_g_kg', 'ufa_g_kg'),
            )
        }),

        ('5. 礦物質 (Minerals)', {
            'classes': ('collapse',),
            'fields': (
                # 常量
                ('calcium_g_per_kg', 'phosphorus_g_per_kg'),
                ('sodium_g_per_kg', 'chloride_g_per_kg', 'potassium_g_per_kg', 'magnesium_g_per_kg'),
                # 微量
                ('iron_mg_per_kg', 'copper_mg_per_kg', 'zinc_mg_per_kg'),
                ('manganese_mg_per_kg', 'selenium_mg_per_kg'),
            )
        }),

        ('6. 磷消化率與有效磷 (Phosphorus Digestibility)', {
            'classes': ('collapse',),
            'fields': (
                
                ('digestible_p_pig_no_phytase_g_kg', 'digestible_p_pig_with_phytase_g_kg'),
                ('available_p_broiler_g_kg', 'available_p_cockerel_g_kg'),                
            )
        }),

        ('7. 維生素 (Vitamins)', {
            'classes': ('collapse',),
            'fields': (
                # 脂溶性
                ('vitamin_a_kiu_kg', 'vitamin_d_kiu_kg', 'vitamin_e_mg_kg', 'vitamin_k_mg_kg'),
                # 水溶性
                ('choline_mg_kg', 'riboflavin_mg_kg', 'niacin_mg_kg'),
                ('pantothenic_acid_mg_kg', 'vitamin_b12_ug_kg', 'folic_acid_mg_kg'),
            )
        }),

        ('8. 總胺基酸 (Total AA)', {
            'classes': ('collapse',),
            'fields': (
                ('lysine_total_g_kg', 'methionine_total_g_kg', 'cystine_total_g_kg', 'met_cys_total_g_kg'),
                ('threonine_total_g_kg', 'tryptophan_total_g_kg', 'valine_total_g_kg'),
                ('isoleucine_total_g_kg', 'leucine_total_g_kg', 'histidine_total_g_kg'),
                ('phenylalanine_total_g_kg', 'tyrosine_total_g_kg'),
                ('arginine_total_g_kg', 'alanine_total_g_kg'),
                ('aspartic_acid_total_g_kg', 'glutamic_acid_total_g_kg'),
                ('glycine_total_g_kg', 'serine_total_g_kg', 'proline_total_g_kg'),
            )
        }),

        ('9. 豬回腸消化胺基酸 (SID Pig AA)', {
            'classes': ('collapse',),
            'fields': (
                ('lysine_sid_pig_g_kg', 'methionine_sid_pig_g_kg', 'met_cys_sid_pig_g_kg'),
                ('threonine_sid_pig_g_kg', 'tryptophan_sid_pig_g_kg', 'valine_sid_pig_g_kg'),
                ('isoleucine_sid_pig_g_kg', 'leucine_sid_pig_g_kg', 'histidine_sid_pig_g_kg'),
                ('arginine_sid_pig_g_kg',),
            )
        }),

        ('10. 家禽 SID 胺基酸 (Poultry SID AA)', {
            'classes': ('collapse',),
            'description': '家禽標準迴腸消化胺基酸',
            'fields': (
                ('lysine_sid_poultry_g_kg', 'methionine_sid_poultry_g_kg', 'cystine_sid_poultry_g_kg', 'met_cys_sid_poultry_g_kg'),
                ('threonine_sid_poultry_g_kg', 'tryptophan_sid_poultry_g_kg', 'valine_sid_poultry_g_kg'),
                ('isoleucine_sid_poultry_g_kg', 'leucine_sid_poultry_g_kg', 'histidine_sid_poultry_g_kg'),
                ('phenylalanine_sid_poultry_g_kg', 'tyrosine_sid_poultry_g_kg', 'phe_tyr_sid_poultry_g_kg'),
                ('arginine_sid_poultry_g_kg', 'alanine_sid_poultry_g_kg'),
                ('aspartic_acid_sid_poultry_g_kg', 'glutamic_acid_sid_poultry_g_kg'),
                ('glycine_sid_poultry_g_kg', 'serine_sid_poultry_g_kg', 'proline_sid_poultry_g_kg'),
            )
        }),
        
        ('其他反芻指標', {
            'classes': ('collapse',),
            'fields': (
                
            )
        }),
    )
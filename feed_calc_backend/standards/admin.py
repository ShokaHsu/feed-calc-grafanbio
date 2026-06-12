from django.contrib import admin
from .models import NutrientStandard

@admin.register(NutrientStandard)
class NutrientStandardAdmin(admin.ModelAdmin):
    # 1. 列表頁顯示 (挑選具代表性的欄位)
    # 注意：這裡把舊的 min_me_kcal_per_kg 換成了 min_me_pig_kcal_per_kg
    list_display = (
        'name', 'species', 'stage', 
        'min_crude_protein_percent', 'min_me_pig_kcal_per_kg', 
        'is_public', 'created_by'
    )
    
    # 2. 篩選器
    list_filter = ('species', 'stage', 'is_public')
    
    # 3. 搜尋
    search_fields = ('name', 'description')
    
    # 4. 編輯頁面分組 (配合新的 Model 結構)
    fieldsets = (
        ('基本分類與權限', {
            'fields': (
                'name', 'species', 'stage', 'description',
                'is_public', 'created_by'
            )
        }),
        ('主要成分限制 (Proximate)', {
            'classes': ('collapse',),
            'fields': (
                'min_dm_percent',
                ('min_crude_protein_percent', 'max_crude_protein_percent'),
                'max_crude_fiber_percent', 'max_crude_fat_percent',
            )
        }),
        ('能量限制 (Energy)', {
            'classes': ('collapse',),
            'fields': (
                'min_de_pig_kcal_per_kg', 'min_me_pig_kcal_per_kg',
                'min_ne_pig_growth_kcal_per_kg', 'min_ne_pig_sow_kcal_per_kg',
                'min_me_broiler_kcal_per_kg', 'min_me_layer_kcal_per_kg',
            )
        }),
        ('總胺基酸限制 (Total AA)', {
            'classes': ('collapse',),
            'fields': (
                'min_lysine_total_g_kg', 'min_methionine_total_g_kg', 'min_met_cys_total_g_kg',
                'min_threonine_total_g_kg', 'min_tryptophan_total_g_kg',
            )
        }),
        ('SID 胺基酸限制 (Pig)', {
            'classes': ('collapse',),
            'fields': (
                'min_lysine_sid_pig_g_kg', 'min_methionine_sid_pig_g_kg', 'min_met_cys_sid_pig_g_kg',
                'min_threonine_sid_pig_g_kg', 'min_tryptophan_sid_pig_g_kg',
            )
        }),

        ('SID 胺基酸限制 (Broiler)', {
            'classes': ('collapse',),
            'fields': (
                'min_lysine_sid_broiler_g_kg', 'min_methionine_sid_broiler_g_kg', 'min_met_cys_sid_broiler_g_kg',
                'min_threonine_sid_broiler_g_kg', 'min_tryptophan_sid_broiler_g_kg',
            )
        }),

        ('礦物質限制 (Minerals)', {
            'classes': ('collapse',),
            'fields': (
                ('min_calcium_g_per_kg', 'max_calcium_g_per_kg'),
                'min_phosphorus_g_per_kg', 'min_available_phosphorus_g_per_kg',
                'min_sodium_g_per_kg',
            )
        }),
    )
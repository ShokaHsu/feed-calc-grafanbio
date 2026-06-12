from decimal import Decimal, InvalidOperation
from typing import Dict, Any
from rest_framework import serializers
from .models import Ingredient
from django.db.models import Q

# 定義所有需要進行數值驗證的欄位名稱
INGREDIENT_NUTRIENT_FIELDS = [
    # 主要成分
    "dm_percent", "crude_protein_percent", "crude_fiber_percent", "crude_fat_percent", 
    "ash_percent", "starch_percent", "sugar_percent", "ndf_percent", "adf_percent",
    
    # 能量
    "de_pig_kcal_per_kg", "me_pig_kcal_per_kg", "ne_pig_growth_kcal_per_kg", "ne_pig_sow_kcal_per_kg",
    "amen_broiler_kcal_per_kg", "amen_cockerel_kcal_per_kg",
    
    # 礦物質
    "calcium_g_per_kg", "phosphorus_g_per_kg", "available_phosphorus_g_per_kg",
    "sodium_g_per_kg", "chloride_g_per_kg", "potassium_g_per_kg", "magnesium_g_per_kg",
    
    # 胺基酸 (Total)
    "lysine_total_g_kg", "methionine_total_g_kg", "cystine_total_g_kg", "met_cys_total_g_kg",
    "threonine_total_g_kg", "tryptophan_total_g_kg", "valine_total_g_kg", 
    "isoleucine_total_g_kg", "leucine_total_g_kg", "histidine_total_g_kg", "arginine_total_g_kg",
    
    # 維生素
    "vitamin_a_kiu_kg", "vitamin_d_kiu_kg", "vitamin_e_mg_kg", "vitamin_k_mg_kg",
    "choline_mg_kg", "riboflavin_mg_kg", "niacin_mg_kg", "pantothenic_acid_mg_kg",
    "vitamin_b12_ug_kg", "folic_acid_mg_kg", "vitamin_b1_mg_kg", "vitamin_b6_mg_kg",
    "biotin_mcg_kg",

    "cost_per_kg_twd"
]

class IngredientSerializer(serializers.ModelSerializer):
    # 顯示建立者名稱
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Ingredient
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by", "is_public", "created_by_name")

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        1. 驗證數值合理性
        2. 驗證會員原料數量限制
        """
        request = self.context.get('request')
        
        # --- [新增] 會員等級數量限制檢查 ---
        # 只在「新增 (Create)」時檢查，修改 (Update) 不檢查
        if request and request.user.is_authenticated and not self.instance:
            user = request.user
            
            # 計算目前已建立的私有原料 (不含系統公用)
            current_count = Ingredient.objects.filter(created_by=user).count()
            
            # 定義各等級上限
            limits = {
                'FREE': 20,        # 免費會員限 20 筆
                'SILVER': 100,     # 銀級會員限 100 筆
                'ENTERPRISE': float('inf') # 企業會員無上限
            }
            
            limit = limits.get(user.tier, 20) # 預設為免費額度
            
            if current_count >= limit:
                tier_name = user.get_tier_display()
                raise serializers.ValidationError(
                    f"您目前的等級 ({tier_name}) 最多只能建立 {limit} 筆自訂原料。請升級會員以解鎖更多額度。"
                )
        # -------------------------------------

        # --- 數值合理性檢查 ---
        errors = {}
        UPPER_LIMITS = {
            "crude_protein_percent": 100, "crude_fiber_percent": 100, "crude_fat_percent": 100,
            "lysine_g_per_kg": 100, "threonine_g_per_kg": 100, "methionine_g_per_kg": 100,
            "calcium_g_per_kg": 400, "phosphorus_g_per_kg": 250,
            "me_kcal_per_kg": 9500, "amen_broiler_kcal_per_kg": 9500,
        }

        for field_name in INGREDIENT_NUTRIENT_FIELDS:
            if field_name in attrs and attrs[field_name] is not None:
                value = attrs[field_name]
                try:
                    dec_value = Decimal(str(value))
                except (ValueError, TypeError, InvalidOperation):
                    errors[field_name] = "格式錯誤，必須是有效的數值。"
                    continue

                if dec_value < 0:
                    errors[field_name] = "數值不可為負數。"
                    continue

                if field_name in UPPER_LIMITS:
                    limit_val = Decimal(str(UPPER_LIMITS[field_name]))
                    if dec_value > limit_val:
                        errors[field_name] = f"數值超過合理上限 ({limit_val})。"

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
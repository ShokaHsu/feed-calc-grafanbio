from rest_framework import serializers
from django.db.models import Q
from .models import Formula, FormulaItem
from accounts.models import Customer
from ingredients.models import Ingredient
from standards.models import NutrientStandard
from .services import FormulaService

# =======================================================
# 1. 最小化 Customer Serializer (用於在 Formula 列表中顯示)
# =======================================================
# 由於我們只在 Formula 列表/詳情中顯示客戶名稱，建立一個最小化 Serializer 避免載入過多資料
class CustomerMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        # 只需要客戶的 ID 和 名稱 (name)
        fields = ('id', 'name')
        
# =======================================================
# 2. 最小化 Standard Serializer (用於在 Formula 列表中顯示)
# =======================================================
# 同理，只顯示標準名稱
class StandardMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutrientStandard
        # 只需要標準的 ID 和 名稱 (name)
        fields = ('id', 'name')

# =======================================================
# 3. Formula Item Serializer (配方明細)
# =======================================================
class FormulaItemSerializer(serializers.ModelSerializer):
    # 透過關聯欄位 Ingredient 獲取名稱，read_only=True
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)

    class Meta:
        model = FormulaItem
        fields = ('id', 'ingredient', 'ingredient_name', 'amount_kg')
        # 如果你還沒建立 IngredientSerializer，確保 ingredient 是 PrimaryKeyRelatedField

# =======================================================
# 4. Formula Serializer (配方主表)
# =======================================================
class FormulaSerializer(serializers.ModelSerializer):
    
    # 讀取用的巢狀欄位 (Read Only)
    customer = CustomerMinimalSerializer(read_only=True, allow_null=True) 
    standard = StandardMinimalSerializer(read_only=True, allow_null=True)
    items = FormulaItemSerializer(many=True, read_only=True) # 保持唯讀，方便 GET 顯示
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    # 寫入用的欄位 (Write Only)
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.none(), source='customer', write_only=True, required=False, allow_null=True
    )
    standard_id = serializers.PrimaryKeyRelatedField(
        queryset=NutrientStandard.objects.all(), source='standard', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Formula
        fields = (
            "id", "name", "description", 
            "customer", "standard", 
            "customer_id", "standard_id", 
            "created_by", "created_by_name", "created_at",
            "batch_size", "total_cost", "cost_per_kg", 
            "items", 
        )
        read_only_fields = ("created_by", "batch_size", "total_cost", "cost_per_kg")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['customer_id'].queryset = Customer.objects.filter(owner=request.user)

    def _get_accessible_ingredients(self, user):
        return Ingredient.objects.filter(Q(is_public=True) | Q(created_by=user))

    def create(self, validated_data):
        """
        覆寫 Create 方法
        """
        # 1. 建立 Formula 主檔
        formula = Formula.objects.create(**validated_data)
        
        # 2. ✨ [關鍵修正] 從原始資料 (initial_data) 獲取 items
        # 因為 items 在上方定義為 read_only=True，所以 validated_data 裡不會有它
        # 我們必須直接拿前端送來的原始 JSON
        items_data = self.initial_data.get('items', [])

        # 3. 建立原料明細 (驗證每筆原料是否在使用者可存取範圍內)
        accessible = self._get_accessible_ingredients(self.context['request'].user)
        for item in items_data:
            ingredient_id = item.get('ingredient')
            amount = item.get('amount_kg')
            if ingredient_id is not None and amount is not None:
                if not accessible.filter(id=ingredient_id).exists():
                    raise serializers.ValidationError(
                        {'items': f'原料 ID {ingredient_id} 不存在或無存取權限'}
                    )
                FormulaItem.objects.create(
                    formula=formula,
                    ingredient_id=ingredient_id,
                    amount_kg=amount
                )
        
        # 4. 觸發計算服務 (算出總重與成本)
        FormulaService.calculate_and_save(formula)
        
        return formula

    def update(self, instance, validated_data):
        """
        覆寫 Update 方法
        """
        # 1. 更新主檔欄位
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 2. ✨ [關鍵修正] 檢查是否有傳送 items 更新
        if 'items' in self.initial_data:
            items_data = self.initial_data.get('items', [])
            
            # 策略：先刪除舊的，再建立新的 (最簡單穩定的做法)
            instance.items.all().delete()
            
            accessible = self._get_accessible_ingredients(self.context['request'].user)
            for item in items_data:
                ingredient_id = item.get('ingredient')
                amount = item.get('amount_kg')
                if ingredient_id is not None and amount is not None:
                    if not accessible.filter(id=ingredient_id).exists():
                        raise serializers.ValidationError(
                            {'items': f'原料 ID {ingredient_id} 不存在或無存取權限'}
                        )
                    FormulaItem.objects.create(
                        formula=instance,
                        ingredient_id=ingredient_id,
                        amount_kg=amount
                    )
            
            # 3. 重新計算
            FormulaService.calculate_and_save(instance)

        return instance
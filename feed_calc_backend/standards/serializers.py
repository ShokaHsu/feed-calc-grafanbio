from rest_framework import serializers
from .models import NutrientStandard

class NutrientStandardSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutrientStandard
        fields = '__all__'
        # 禁止前端直接修改擁有者或系統屬性
        read_only_fields = ('id', 'created_by', 'is_public', 'created_at', 'updated_at')
    
    def validate(self, attrs):
        request = self.context.get('request')
        
        # 1. 檢查是否為新增操作
        if request and request.method == 'POST':
            user = request.user
            
            # 2. 檢查會員等級
            # 假設 'FREE' 是免費會員，'SILVER' 和 'ENTERPRISE' 是付費會員
            if not user.is_authenticated:
                raise serializers.ValidationError("請先登入才能建立標準。")
                
            # 如果不是付費會員，拒絕建立
            if user.tier == 'FREE' and not user.is_superuser:
                raise serializers.ValidationError({
                    "detail": "您的會員等級 (免費會員) 無法建立自訂標準。請升級為銀級或企業會員。"
                })
                
            # (選用) 限制數量：例如銀級只能建 3 個，企業無限
            if user.tier == 'SILVER':
                count = NutrientStandard.objects.filter(created_by=user).count()
                if count >= 3:
                    raise serializers.ValidationError("銀級會員最多只能建立 10 個自訂標準。")

        return attrs
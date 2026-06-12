from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator # ✨ 引入唯一性驗證器
from .models import Customer, UserPreference

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    # ✨ [修改] 顯式定義 email 欄位：必填 + 唯一性檢查
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="此 Email 已經被註冊過了")]
    )
    
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'], # 這裡現在一定會有值
            password=validated_data['password']
        )
        return user
    
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'city', 'species', 'scale', 'contact_name', 'phone', 'address']
        read_only_fields = ['owner'] # 擁有者由後端自動設定

class UserPreferenceSerializer(serializers.ModelSerializer):
    favorites = serializers.JSONField(source='favorite_ingredients')
    nutrient_display_mode = serializers.CharField()

    class Meta:
        model = UserPreference
        fields = ['favorites', 'nutrient_display_mode']
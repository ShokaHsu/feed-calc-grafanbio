from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from .models import Customer, UserPreference
from .serializers import UserRegistrationSerializer, CustomerSerializer, UserPreferenceSerializer

User = get_user_model()

# ==========================================
# 1. 使用者註冊 API (RegisterView)
# ==========================================
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny] # 允許任何人註冊
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        # 覆寫 create 方法，讓註冊成功後直接回傳 Token
        response = super().create(request, *args, **kwargs)
        
        user = User.objects.get(username=response.data['username'])
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        }, status=status.HTTP_201_CREATED)

# ==========================================
# 2. 客戶/牧場管理 API (CustomerListView)
# ==========================================
class CustomerListView(generics.ListCreateAPIView):
    # 這裡處理 GET (列表) 和 POST (新增客戶)
    permission_classes = [permissions.IsAuthenticated] # 必須登入才能操作客戶資料
    serializer_class = CustomerSerializer
    
    def get_queryset(self):
        # 查詢集：只顯示當前使用者所擁有的客戶資料
        if self.request.user.is_authenticated:
            return Customer.objects.filter(owner=self.request.user).order_by('name')
        
        # 雖然 permission_classes 已經擋掉未登入者，但這裡仍需保護
        return Customer.objects.none() 

    def perform_create(self, serializer):
        # 執行建立：自動將客戶的 owner 欄位設為當前登入者
        serializer.save(owner=self.request.user)


class UserPreferenceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        pref, _ = UserPreference.objects.get_or_create(user=request.user)
        serializer = UserPreferenceSerializer(pref)
        return Response(serializer.data)

    def post(self, request):
        pref, _ = UserPreference.objects.get_or_create(user=request.user)
        favorites = request.data.get('favorites', pref.favorite_ingredients)
        mode = request.data.get('nutrient_display_mode', pref.nutrient_display_mode)

        pref.favorite_ingredients = favorites
        pref.nutrient_display_mode = mode
        pref.save()

        serializer = UserPreferenceSerializer(pref)
        return Response(serializer.data)
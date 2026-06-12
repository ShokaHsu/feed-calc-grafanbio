from django.contrib.auth import get_user_model 
from rest_framework import authentication

class DesktopStandaloneAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header == 'Bearer standalone-admin':
            User = get_user_model() # 延遲獲取 User 模型，避免循環引用
            
            # 建立或取得單機使用者
            user, created = User.objects.get_or_create(
                username='desktop_default_user',
                defaults={
                    'is_staff': False, 
                    'is_superuser': False,
                    'email': 'local@desktop.app' # 確保這裡符合你的 EmailField 格式
                }
            )
            return (user, None)
        return None
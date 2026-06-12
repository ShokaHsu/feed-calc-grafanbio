# accounts/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailOrUsernameBackend(ModelBackend):
    """允許用 username 或 email 登入"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)

        user = None
        # 先用 username 找
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 再用 email（不分大小寫）找
            try:
                user = User.objects.get(email__iexact=username)
            except User.DoesNotExist:
                return None

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

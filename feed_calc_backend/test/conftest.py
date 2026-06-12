import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    User = get_user_model()
    # 同時建立 username 與 email，讓兩種登入方式都可測
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="pass1234"
    )

@pytest.fixture
def auth_client(api_client, user):
    """
    盡量拿到 Bearer token：
    1) 先試 username/password
    2) 失敗再試 email/password
    3) 都失敗則 fallback 用 session login（僅供需要認證但未強制 JWT 的情境）
    """
    # 試 1：username
    resp = api_client.post("/api/auth/token/", {
        "username": user.username,
        "password": "pass1234",
    }, format="json")
    if resp.status_code == 200 and "access" in resp.data:
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
        return api_client

    # 試 2：email
    resp = api_client.post("/api/auth/token/", {
        "email": user.email,
        "password": "pass1234",
    }, format="json")
    if resp.status_code == 200 and "access" in resp.data:
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
        return api_client

    # 試 3：session login（僅作保底）
    api_client.login(username=user.username, password="pass1234")
    return api_client

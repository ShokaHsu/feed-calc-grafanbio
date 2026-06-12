# config/settings/prod.py
from .base import *
import dj_database_url
import os

# 1. DEBUG
DEBUG = False

# 2. ALLOWED_HOSTS
# Railway 會分配一個 xxx.up.railway.app 的網址，建議用 '*' 或者具體網址
ALLOWED_HOSTS = [
    'feed-calc-project-production.up.railway.app',
    'healthcheck.railway.app',
]

# 3. CSRF Trusted Origins (Railway 必須設定這個！)
# 這是 Render 不需要但 Railway 需要的
CSRF_TRUSTED_ORIGINS = [
    'https://feed-calc-project-production.up.railway.app',
    'https://feed-calc-project.vercel.app',
]

# [安全性] 強制 Cookie 使用 HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# 4. 資料庫
# ✨ [修正] 資料庫設定：優先讀取環境變數，若無則退回 SQLite
database_url = os.environ.get('DATABASE_URL')

if database_url:
    # 雲端環境 (Render/Railway)
    DATABASES = {
        'default': dj_database_url.config(
            default=database_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # 本地打包環境 (.exe) 或開發測試
    print("⚠️ DATABASE_URL not found, using local SQLite.")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# 5. 靜態檔案 (WhiteNoise)
# Insert after SecurityMiddleware (index 2), not before it
if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.insert(2, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Railway only serves the API — no frontend dist folder here
STATICFILES_DIRS = []
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# 6. CORS
# Safe with token auth — CSRF attacks don't apply to Authorization header tokens.
# All sensitive endpoints are protected by IsAuthenticated regardless of origin.
CORS_ALLOW_ALL_ORIGINS = True

# 7. HTTPS (Railway terminates SSL at its proxy)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'           # 或其他 SMTP 服務商
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')         # 例如: yourname@gmail.com
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD') # 例如: Gmail 應用程式密碼
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
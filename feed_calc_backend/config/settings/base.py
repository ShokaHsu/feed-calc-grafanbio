"""
Django settings for feed-calc-backend project.
Base settings to be imported by dev.py or prod.py
"""

from pathlib import Path
from decouple import config  # 使用 python-decouple 讀取 .env
import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# 因為你的結構是 config/settings/base.py，所以要往上找三層回到根目錄
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# 必須在環境變數中設定 SECRET_KEY，缺少時提供預設值以利單機版啟動
SECRET_KEY = config('SECRET_KEY', default='django-insecure-fallback-key-for-standalone-desktop-app-12345')

# DEBUG 和 ALLOWED_HOSTS 通常在 dev.py 或 prod.py 覆寫，這裡留預設
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    # --- Django 內建 (保持原樣) ---
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # --- 第三方套件 (保持原樣) ---
    'rest_framework',
    'corsheaders',
    'django_filters',
    'rest_framework.authtoken', # dj-rest-auth 需要
    
    'djoser',
    
    
    # --- 想要支援的第三方登入 ---
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google', # ✨ Google
    'allauth.socialaccount.providers.line',   # ✨ LINE

    # --- C. dj-rest-auth (連接 Allauth 與 API 的橋樑) ---
    'dj_rest_auth',
    'dj_rest_auth.registration', # 處理註冊邏輯與 Social Login

    # --- 本地 Apps (請補上下面這些) ---
    'common',        # 你的 TimeStampedModel 可能在這裡
    'accounts',      # 會員管理
    'ingredients',   # 原料管理 (已存在)
    'standards',     # 營養標準 
    'formulas',      # 配方計算
   
]

# 必須設定 Site ID，通常開發環境是 1
SITE_ID = 1

# ==========================================
# Allauth 帳號設定
# ==========================================

# 1. 登入方式 

ACCOUNT_LOGIN_METHODS = {'email'} 

# 2. 註冊欄位 
ACCOUNT_SIGNUP_FIELDS = [
    'username',    # 登入用，預設必填
    'email*',      # 加了 '*' 代表必填 (取代 ACCOUNT_EMAIL_REQUIRED=True)
    'password1*',  # (選填) 如果您想顯式控制密碼欄位，也可以寫進來
]

# 3. 其他保持不變的設定
ACCOUNT_EMAIL_VERIFICATION = 'none' # 開發階段暫時不驗證
ACCOUNT_UNIQUE_EMAIL = True         # Email 必須唯一

# 4. 黑名單
ACCOUNT_USERNAME_BLACKLIST = ['admin', 'root', 'superuser']


MIDDLEWARE = [
    
    
    # [新增] CORS Middleware 必須放在 CommonMiddleware 之前，建議放在最上面
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'config.urls'

# 在 base.py 中，我們只保留開發環境的路徑
FRONTEND_DIST = BASE_DIR.parent / 'feed_calc_frontend' / 'dist'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [FRONTEND_DIST], # 如果有全域 template 資料夾可加在這裡
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# 預設使用 SQLite，方便開發
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n
LANGUAGE_CODE = 'zh-hant'  # 設定為繁體中文
TIME_ZONE = 'Asia/Taipei'  # 設定為台北時間
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # 收集靜態檔案的位置

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- Django REST Framework 設定 ---
REST_FRAMEWORK = {
    # 設定驗證方式：優先檢查 Token
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 1. 標準 Token 驗證 (給 Djoser / 舊版客戶端用)
        'rest_framework.authentication.TokenAuthentication',
        # 2. JWT 驗證 (給雲端版前端用)
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # DesktopStandaloneAuthentication 僅在 desktop.py 中啟用，不得出現在此處
    ],
    
    # 設定預設權限
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# 3. Authentication Backends (第三方認證登入)
AUTHENTICATION_BACKENDS = [
    # 允許用 username 或 email 登入
    'accounts.backends.EmailOrUsernameBackend',

    # Allauth 驗證 (第三方登入必要)
    'allauth.account.auth_backends.AuthenticationBackend',
]

AUTH_USER_MODEL = 'accounts.User'

# 靜態檔案路徑 (指向前端 dist/assets)
STATICFILES_DIRS = [
    FRONTEND_DIST,
]
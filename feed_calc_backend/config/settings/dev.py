from .base import *
DEBUG = True
TIME_ZONE = "Asia/Taipei"
USE_TZ = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
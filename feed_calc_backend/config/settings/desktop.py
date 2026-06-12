# config/settings/desktop.py
from .base import *
import sys
import os
import shutil
from pathlib import Path
from rest_framework.authentication import BaseAuthentication

DEBUG = False
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

CORS_ALLOW_ALL_ORIGINS = True

from corsheaders.defaults import default_headers
CORS_ALLOW_HEADERS = list(default_headers) + ['x-client-mode']

# 針對 PyInstaller 打包環境處理路徑
if getattr(sys, 'frozen', False):
    # 打包後：將資料庫存放在 C:\Users\使用者名稱\AppData\Roaming\FeedCalc\
    app_data_dir = Path(os.getenv('APPDATA')) / 'FeedCalc'
    try:
        app_data_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        # 如果無法存取 APPDATA，退而求其次使用執行檔目錄
        app_data_dir = Path(sys.executable).parent / 'data'
        app_data_dir.mkdir(parents=True, exist_ok=True)

    DB_PATH = app_data_dir / 'db.sqlite3'
    
    # 取得打包進去的預設資料庫路徑
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    bundled_db = Path(base_path) / 'db.sqlite3'

    # 診斷用 log 檔 — 確認 DB 初始化流程
    _log = app_data_dir / 'startup.log'
    def _dblog(msg):
        print(msg, flush=True)
        with open(_log, 'a', encoding='utf-8') as _f:
            _f.write(msg + '\n')

    _dblog(f"[startup] frozen={getattr(sys, 'frozen', False)}")
    _dblog(f"[startup] _MEIPASS={getattr(sys, '_MEIPASS', 'NOT SET')}")
    _dblog(f"[startup] bundled_db={bundled_db}")
    _dblog(f"[startup] bundled_db.exists()={bundled_db.exists()}")
    if bundled_db.exists():
        _dblog(f"[startup] bundled_db size={bundled_db.stat().st_size} bytes")
    _dblog(f"[startup] DB_PATH={DB_PATH}")
    _dblog(f"[startup] DB_PATH.exists()={DB_PATH.exists()}")
    if DB_PATH.exists():
        _dblog(f"[startup] DB_PATH size={DB_PATH.stat().st_size} bytes")

    # Copy bundled DB if:
    #   1. APPDATA DB doesn't exist yet (fresh install), OR
    #   2. APPDATA DB is smaller than the bundled DB (empty/stale from a failed previous run)
    if bundled_db.exists():
        needs_copy = (
            not DB_PATH.exists() or
            DB_PATH.stat().st_size < bundled_db.stat().st_size
        )
        if needs_copy:
            _dblog(f"[startup] ACTION: copying bundled DB → {DB_PATH}")
            shutil.copy2(bundled_db, DB_PATH)
            _dblog(f"[startup] copy done, final size={DB_PATH.stat().st_size} bytes")
        else:
            _dblog("[startup] ACTION: using existing DB (same size or larger, skipping copy)")
    else:
        _dblog("[startup] ERROR: bundled DB not found — Django will create empty DB")
else:
    # 開發中：維持在專案資料夾下
    DB_PATH = BASE_DIR / 'db.sqlite3'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_PATH,
    }
}


class StandaloneBypassAuth(BaseAuthentication):
    def authenticate(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        # 軟體啟動時，自動取得或建立一個擁有最高權限的本機帳號
        user, _ = User.objects.get_or_create(
            username="local_admin",
            defaults={"is_superuser": True, "is_staff": True}
        )
        # 欺騙 Django，說這個請求就是這個最高權限管理員發出的
        return (user, None)

# 抓取 base.py 中原有的 DRF 設定，並覆寫認證機制
DRF_SETTINGS = locals().get('REST_FRAMEWORK', {})
DRF_SETTINGS['DEFAULT_AUTHENTICATION_CLASSES'] = [
    'config.settings.desktop.StandaloneBypassAuth',
]
# 如果有些 API 寫死了權限檢查，這行可以確保通行無阻
DRF_SETTINGS['DEFAULT_PERMISSION_CLASSES'] = [
    'rest_framework.permissions.AllowAny',
]
REST_FRAMEWORK = DRF_SETTINGS
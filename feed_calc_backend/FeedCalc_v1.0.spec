
import os
import sys
from PyInstaller.utils.hooks import collect_all

# 1. 設定專案根目錄 (確保能找到 config)
sys.path.insert(0, os.path.abspath('.'))

# 2. 指定 Django 設定檔 (這是解決 ROOT_URLCONF 的關鍵)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['manage.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../feed-calc-frontend/dist', 'feed-calc-frontend/dist'),
        ('db.sqlite3', '.'),], # 把預設資料庫包進去 (選用)
    hiddenimports=[
        'config.settings.prod',
        'config.urls',
        'config.settings.base',  # 基礎設定
        'config.settings.dev',   # 開發設定 (雖然打包不用，但避免報錯可加上)
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'rest_framework',
        'corsheaders',
        'whitenoise.middleware', # 如果你有用 whitenoise
        # 加入你的 apps
        'accounts', 'ingredients', 'standards', 'formulas', 'common'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FeedCalc_v1.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

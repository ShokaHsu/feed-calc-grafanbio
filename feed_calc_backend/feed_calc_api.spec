# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 1. 設定環境變數
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.desktop'

# 2. 收集 Django 必要的資料檔 (Templates, Static, etc.)
django_datas = collect_data_files('django')
rest_datas = collect_data_files('rest_framework')
djoser_datas = collect_data_files('djoser')

# 3. 收集動態 URL 套件的所有子模組 (PyInstaller 無法靜態追蹤 include('djoser.urls') 這類字串)
djoser_hiddens    = collect_submodules('djoser')
allauth_hiddens   = collect_submodules('allauth')
dj_rest_hiddens   = collect_submodules('dj_rest_auth')

a = Analysis(
    ['run_api.py'],
    pathex=[os.getcwd()],
    binaries=[],
    datas=[
        ('db.sqlite3', '.'),  # 強制包含資料庫 (schema + migrations baseline)
        ('.env', '.'),        # 包含環境變數檔 (雖然我們有 fallback，但包含它比較保險)
        ('ingredients/fixtures/crawled_seed.json', 'ingredients/fixtures'),  # 原料種子資料
    ] + django_datas + rest_datas + djoser_datas,
    hiddenimports=[
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.sites',
        'rest_framework',
        'rest_framework.authtoken',
        'corsheaders',
        'django_filters',
        'waitress',
        'config.settings.desktop',
        'accounts',
        'ingredients',
        'standards',
        'formulas',
        'common',
    ] + djoser_hiddens + allauth_hiddens + dj_rest_hiddens,
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
    name='feed_calc_api',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True, # 暫時開啟 Console 以利診斷
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

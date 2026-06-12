#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import hashlib
import subprocess
import webbrowser
from threading import Timer

# # ✨ [設定] 秘密鹽值 (隨便打一串亂碼)
# SECRET_SALT = "Feed_Calc_2025_Secret_Key_!@#$"

# def get_hwid():
#     """獲取 Windows 電腦的唯一硬體 ID (主機板序號)"""
#     try:
#         # 只有在 Windows 下才執行 wmic，避免 Linux (Render) 報錯
#         if sys.platform == 'win32':
#             cmd = 'wmic csproduct get uuid'
#             uuid = subprocess.check_output(cmd).decode().split('\n')[1].strip()
#             return uuid
#         return "NON_WINDOWS_HOST"
#     except Exception:
#         # 如果獲取失敗 (例如非 Windows)，回傳一個錯誤標記或 fallback
#         return "UNKNOWN_MACHINE_ID"

# def verify_license():
#     """檢查授權檔案 (僅在打包環境下執行)"""
#     # 開發環境或雲端部署直接略過
#     if not getattr(sys, 'frozen', False):
#         return

#     hwid = get_hwid()
#     # 簡單防呆，如果讀不到 ID 就跳過或報錯
#     if hwid == "NON_WINDOWS_HOST":
#         return

#     expected_key = hashlib.sha256((hwid + SECRET_SALT).encode()).hexdigest()
#     license_file = 'license.key'

#     if not os.path.exists(license_file):
#         print("\n" + "="*60)
#         print("⛔ 軟體尚未授權 (License Not Found)")
#         print(f"您的機器碼 (Machine ID): {hwid}")
#         print("請複製上方機器碼，傳送給管理員以獲取授權檔案 (license.key)。")
#         print("="*60 + "\n")
#         input("按 Enter 鍵離開...")
#         sys.exit(1)

#     with open(license_file, 'r') as f:
#         user_key = f.read().strip()

#     if user_key != expected_key:
#         print("\n" + "="*60)
#         print("❌ 授權無效 (Invalid License)")
#         print(f"您的機器碼 (Machine ID): {hwid}")
#         print("="*60 + "\n")
#         input("按 Enter 鍵離開...")
#         sys.exit(1)
    
#     print("✅ 授權驗證成功！正在啟動系統...")

def open_browser():
    """自動開啟瀏覽器"""
    webbrowser.open_new("http://127.0.0.1:8000/")

def main():
    """Run administrative tasks."""
    # 預設使用生產環境設定
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
# C:\05_sideproject\feed-calc-backend\test\test_auth.py
import os
import json
import textwrap
import requests
from typing import Tuple, Any, Optional

BASE = os.environ.get("API_BASE", "http://127.0.0.1:8000/api")
USERNAME = os.environ.get("API_USER", "fafa")   # ← 改成你的帳號
PASSWORD = os.environ.get("API_PASS", "141319")   # ← 改成你的密碼
EMAIL    = os.environ.get("API_EMAIL", "myelroy@gmail.com") # ← 改成你的Email

def safe_json(resp: requests.Response) -> Tuple[int, Any, Optional[str]]:
    status = resp.status_code
    try:
        return status, resp.json(), None
    except Exception:
        txt = (resp.text or "")[:200]
        return status, None, txt

def pretty(title: str, payload: Any):
    print(f"\n=== {title} ===")
    if isinstance(payload, (dict, list)):
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(payload)

def login() -> Tuple[Optional[str], Optional[str]]:
    url = f"{BASE}/auth/token/"
    body = {"username": USERNAME, "password": PASSWORD, "email": EMAIL}
    resp = requests.post(url, json=body, timeout=10)
    status, js, txt = safe_json(resp)
    pretty("Login Status", status)
    if js is not None: pretty("Login JSON", js)
    if txt is not None: pretty("Login Text", txt)
    if status != 200 or not js or "access" not in js:
        print("\n[ERROR] 登入失敗，請檢查帳密/Email 與後端路由 /auth/token/ 是否正確。")
        return None, None
    return js.get("access"), js.get("refresh")

def call_profile(access: str) -> Optional[requests.Response]:
    url = f"{BASE}/auth/profile"
    return requests.get(url, headers={"Authorization": f"Bearer {access}"}, timeout=10)

def refresh_access(refresh: str) -> Optional[str]:
    url = f"{BASE}/auth/token/refresh/"
    resp = requests.post(url, json={"refresh": refresh}, timeout=10)
    status, js, txt = safe_json(resp)
    pretty("Refresh Status", status)
    if js is not None: pretty("Refresh JSON", js)
    if txt is not None: pretty("Refresh Text", txt)
    if status == 200 and js and "access" in js:
        return js["access"]
    print("\n[ERROR] refresh 失敗；refresh token 可能過期或路由未正確設定。")
    return None

def main():
    print(textwrap.dedent(f"""
    ---------- AUTH FLOW SMOKE TEST ----------
    BASE     : {BASE}
    USERNAME : {USERNAME}
    EMAIL    : {EMAIL}
    （可用環境變數覆蓋：API_BASE / API_USER / API_PASS / API_EMAIL）
    ------------------------------------------
    """).strip())

    # 1) 登入取得 access/refresh
    access, refresh = login()
    if not access:
        return

    # 2) 打 /auth/profile
    resp = call_profile(access)
    if resp is None:
        print("\n[ERROR] 無法連線到後端，請確認 runserver 與埠號。")
        return
    status, js, txt = safe_json(resp)
    pretty("Profile Status", status)
    if js is not None: pretty("Profile JSON", js)
    if txt is not None: pretty("Profile Text", txt)

    # 如果 access 已過期 → refresh 後重試
    if status == 401 and refresh:
        print("\n[Info] access 可能過期，嘗試 refresh 後重試…")
        new_access = refresh_access(refresh)
        if new_access:
            resp2 = call_profile(new_access)
            if resp2 is not None:
                st2, js2, txt2 = safe_json(resp2)
                pretty("Profile (after refresh) Status", st2)
                if js2 is not None: pretty("Profile (after refresh) JSON", js2)
                if txt2 is not None: pretty("Profile (after refresh) Text", txt2)

if __name__ == "__main__":
    main()

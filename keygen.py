import hashlib

# ⚠️ 必須跟 manage.py 裡面的鹽值一模一樣
SECRET_SALT = "Feed_Calc_2025_Secret_Key_!@#$"

def generate_key():
    print("=== 飼料配方軟體 金鑰產生器 ===")
    hwid = input("請輸入客戶的機器碼 (Machine ID): ").strip()
    
    if not hwid:
        print("❌ 機器碼不能為空")
        return

    # 產生金鑰
    license_key = hashlib.sha256((hwid + SECRET_SALT).encode()).hexdigest()
    
    print("\n✅ 產生金鑰如下 (請複製並存為 license.key 給客戶):")
    print("-" * 60)
    print(license_key)
    print("-" * 60)
    
    # 自動產檔方便
    with open('license.key', 'w') as f:
        f.write(license_key)
    print(f"已自動產生 license.key 檔案。")

if __name__ == "__main__":
    generate_key()
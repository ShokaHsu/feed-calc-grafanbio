import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from ingredients.models import Ingredient
import math
import os


# --- 輔助函式：確保數值轉換安全 ---
def _to_float(x):
    try:
        if x is None or (isinstance(x, float) and math.isnan(x)):
            return None
        return float(x)
    except Exception:
        return None
    
# 分類對照表
# --- 分類代碼對照表 ---
CATEGORY_SLUG_MAP = {
    '能量': 'ENERGY', 'ENERGY': 'ENERGY',
    '蛋白原料': 'PROTEIN', 'PROTEIN': 'PROTEIN',
    '植物來源': 'PLANT_RESOURCES', 'PLANT_RESOURCES': 'PLANT_RESOURCES',
    '動物來源': 'ANIMAL_RESOURCES', 'ANIMAL_RESOURCES': 'ANIMAL_RESOURCES',
    '礦物質': 'MINERAL', 'MINERAL': 'MINERAL',
    '添加劑': 'ADDITIVE', 'ADDITIVE': 'ADDITIVE',
    '胺基酸': 'AMINO_ACID', 'AMINO_ACID': 'AMINO_ACID',
    '其他': 'OTHER', 'OTHER': 'OTHER',
}

# --- 欄位對照表 ---
# 這裡應該包含所有你的 Excel 欄位對應到 Model 欄位的關係
COLUMNS_MAP = {
    'Category': 'category',
    'Cost': 'cost_per_kg_twd',
    
    # 主要成分
    'Crude_Protein': 'crude_protein_percent',
    'Crude_Fiber': 'crude_fiber_percent',
    'Crude_Fat': 'crude_fat_percent',
    
    # 能量 (假設 Excel 的 ME 是豬的 ME)
    'ME': 'me_pig_kcal_per_kg', 
    'AMEn broiler kcal/kg': 'amen_broiler_kcal_per_kg',
    
    # 胺基酸 (Total)
    # 注意：你需要確認 Excel 裡的 Lysine 是 Total 還是 SID
    # 假設 Excel 是 Total：
    'Lysine g/kg': 'lysine_total_g_kg',
    'Threonine g/kg': 'threonine_total_g_kg',
    'MET g/kg': 'methionine_total_g_kg',
    'CYS g/kg': 'cystine_total_g_kg',
    'MET+CYS g/kg': 'met_cys_total_g_kg',
    'TRY g/kg': 'tryptophan_total_g_kg',
   

    # 礦物質
    'Ca g/kg': 'calcium_g_per_kg',
    'P g/kg': 'phosphorus_g_per_kg',
    'Available_Phosphorus': 'available_p_broiler_g_kg',
    
    # 如果 Excel 還有其他欄位，請在此補上對應的新 Model 欄位名稱
}

class Command(BaseCommand):
    help = '從 Excel 的 [營養成分] 分頁匯入資料 (精確標題版)'

    def handle(self, *args, **options):
        # Resolve path relative to this file so it works regardless of CWD
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        excel_path = os.path.join(BASE_DIR, 'feed_database.xlsx')
        sheet_name = '營養成分' # 根據你的 Log，使用 '營養成分' Sheet

        if not os.path.exists(excel_path):
            self.stdout.write(self.style.ERROR(f'找不到檔案: {excel_path}'))
            return

        self.stdout.write(f'正在讀取檔案: {excel_path} ...')

        try:
            df = pd.read_excel(excel_path, sheet_name=sheet_name, engine='openpyxl')
            
            # 清理欄位名稱 (移除前後空白)
            df.columns = [c.strip() for c in df.columns]

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'讀取 Excel 失敗: {str(e)}'))
            return
        
        self.stdout.write(self.style.WARNING(f"偵測到的欄位標題: {list(df.columns)}"))

        # 🚨 [修正 2] 必須定義 join_key，確保它在作用域內
        join_key = 'Ingredient_Name'
        if join_key not in df.columns:
            # 容錯處理：如果 Excel 沒抓到表頭，用 Unnamed: 0 或 Name
            if 'Unnamed: 0' in df.columns:
                join_key = 'Unnamed: 0'
            elif 'Name' in df.columns:
                join_key = 'Name'
            else:
                 self.stdout.write(self.style.ERROR(f"❌ 找不到原料名稱欄位 ({join_key})。請檢查 Excel 標題。"))
                 return

        # ----------------------------------------------------
        # 4. 開始處理每一行
        # ----------------------------------------------------
        
        success_count = 0
        update_count = 0
        name_val = "N/A" # 初始化 name_val，避免 UnboundLocalError

        for index, row in df.iterrows():
            try:
                # 🚨 讀取原料名稱 (第一個崩潰點的修正)
                name_val = row.get(join_key)
                
                if not name_val or str(name_val).lower() == 'nan' or str(name_val).strip() == '':
                    continue
                
                # 初始化 Payload
                payload = {
                    "is_public": True, # 預設為公開的系統原料
                    "created_by": None, # 系統建立
                }

                # 遍歷欄位對照表
                for excel_col, model_col in COLUMNS_MAP.items():
                    if excel_col in df.columns:
                        raw_val = row.get(excel_col)
                        
                        if raw_val is not None:
                            if model_col == 'category':
                                # ✨ 關鍵修正：將 Category 轉為大寫代碼
                                raw_val = str(raw_val).strip().upper()
                                payload[model_col] = CATEGORY_SLUG_MAP.get(raw_val, 'OTHER')
                            
                            else:
                                # 數值欄位
                                val = _to_float(raw_val)

                                # [單位換算檢查] 假設所有 g/kg 欄位如果值很小，需*1000
                                if model_col.endswith("_g_per_kg") and val is not None and val < 20 and 'g/kg' not in excel_col:
                                    val = val * 10
                                
                                payload[model_col] = val

                # 5. 執行資料庫寫入：有則更新，無則新增
                obj, is_created = Ingredient.objects.update_or_create(
                    name=name_val,
                    defaults=payload
                )

                if is_created:
                    success_count += 1
                else:
                    update_count += 1
            
            except Exception as e:
                # 這裡的錯誤處理現在不會再崩潰了
                safe_name = str(name_val).encode('ascii', errors='replace').decode('ascii')
                self.stdout.write(self.style.WARNING(f'Import error: {safe_name} - {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'--- 結束 ---'))
        self.stdout.write(self.style.SUCCESS(f'匯入完成！新增: {success_count} 筆，更新: {update_count} 筆。'))
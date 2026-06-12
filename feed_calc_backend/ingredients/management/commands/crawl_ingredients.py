import requests
import pandas as pd
import re
import time
import io
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from ingredients.models import Ingredient
# 請確認已安裝套件: pip install deep-translator
from deep_translator import GoogleTranslator

class Command(BaseCommand):
    help = '爬取 FeedTables 資料，自動翻譯名稱並寫入資料庫'

    # ================= 設定區 =================
    BASE_URL = "https://feedtables.com"
    PROFILE_URL = "https://feedtables.com/content/table-parameter-profile"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # 初始化翻譯器
    translator = GoogleTranslator(source='auto', target='zh-TW')

    # 行業術語修正字典
    TERM_FIXES = {
        "Meal": "粕", "Distillers grains": "酒糟", "Dehydrated": "脫水",
        "Dried": "乾燥", "Fresh": "新鮮", "Silage": "青貯",
        "Gluten feed": "麩皮", "Gluten meal": "蛋白粉", "Maize": "玉米",
        "Wheat": "小麥", "Barley": "大麥", "Sorghum": "高粱",
        "Soybean": "大豆", "Rapeseed": "油菜籽", "Fish meal": "魚粉",
    }

    # 欄位對應表
    FIELD_MAPPING = {
        # --- 1. 主要成分 (%) ---
        "Dry matter": {"field": "dm_percent", "factor": 1},
        "Crude protein": {"field": "crude_protein_percent", "factor": 1},
        "Crude fibre": {"field": "crude_fiber_percent", "factor": 1},
        "Crude fat": {"field": "crude_fat_percent", "factor": 1},
        "Ash": {"field": "ash_percent", "factor": 1},
        "Starch, enzymatic method": {"field": "starch_percent", "factor": 1},
        "Total sugars": {"field": "sugar_percent", "factor": 1},
        "NDF": {"field": "ndf_percent", "factor": 1},
        "ADF": {"field": "adf_percent", "factor": 1},

        # --- 2. 能量 (kcal/kg) ---
        # 豬 (Pig)
        "DE growing pig (kcal)": {"field": "de_pig_kcal_per_kg", "factor": 1},
        "ME growing pig (kcal)": {"field": "me_pig_kcal_per_kg", "factor": 1},
        "NE growing pig (kcal)": {"field": "ne_pig_growth_kcal_per_kg", "factor": 1},
        "NE adult pig (kcal)": {"field": "ne_pig_sow_kcal_per_kg", "factor": 1},
        
        # 家禽 (Poultry)
        "AMEn broiler (kcal)": {"field": "amen_broiler_kcal_per_kg", "factor": 1},
        "AMEn cockerel (kcal)": {"field": "amen_cockerel_kcal_per_kg", "factor": 1},

        # 反芻 (Ruminant)
        "TDN 1x ruminants NRC 2001": {"field": "tdn_percent", "factor": 1},
        "ME ruminants INRA 2018 (kcal)": {"field": "me_ruminant_kcal_per_kg", "factor": 1},
        "NE meat production ruminants INRA 2018 (kcal)": {"field": "ne_ruminant_kcal_per_kg", "factor": 1},

        # --- 3. 礦物質 ---
        # 常量
        "Calcium": {"field": "calcium_g_per_kg", "factor": 1},
        "Phosphorus": {"field": "phosphorus_g_per_kg", "factor": 1},
        "Sodium": {"field": "sodium_g_per_kg", "factor": 1},
        "Chlorine": {"field": "chloride_g_per_kg", "factor": 1},
        "Potassium": {"field": "potassium_g_per_kg", "factor": 1},
        "Magnesium": {"field": "magnesium_g_per_kg", "factor": 1},
        
        # 微量
        "Iron": {"field": "iron_mg_per_kg", "factor": 1}, 
        "Copper": {"field": "copper_mg_per_kg", "factor": 1},
        "Manganese": {"field": "manganese_mg_per_kg", "factor": 1},
        "Zinc": {"field": "zinc_mg_per_kg", "factor": 1},
        "Selenium": {"field": "selenium_mg_per_kg", "factor": 1},

        # 消化磷
        "Digestible P pig (no phytase)": {"field": "digestible_p_pig_no_phytase_g_kg", "factor": 1},
        "Digestible P pig (with phytase)": {"field": "digestible_p_pig_with_phytase_g_kg", "factor": 1},
        "Available P cockerel": {"field": "available_p_cockerel_g_kg", "factor": 1},
        "Available P broiler": {"field": "available_p_broiler_g_kg", "factor": 1},

        # --- 4. 總胺基酸 (Total AA) --- 
        "Lysine": {"field": "lysine_total_g_kg", "factor": 1},
        "Methionine": {"field": "methionine_total_g_kg", "factor": 1},
        "Cystine": {"field": "cystine_total_g_kg", "factor": 1},
        "Methionine + cystine": {"field": "met_cys_total_g_kg", "factor": 1},
        "Threonine": {"field": "threonine_total_g_kg", "factor": 1},
        "Tryptophan": {"field": "tryptophan_total_g_kg", "factor": 1},
        "Valine": {"field": "valine_total_g_kg", "factor": 1},
        "Isoleucine": {"field": "isoleucine_total_g_kg", "factor": 1},
        "Leucine": {"field": "leucine_total_g_kg", "factor": 1},
        "Phenylalanine": {"field": "phenylalanine_total_g_kg", "factor": 1},
        "Tyrosine": {"field": "tyrosine_total_g_kg", "factor": 1},
        "Histidine": {"field": "histidine_total_g_kg", "factor": 1},
        "Arginine": {"field": "arginine_total_g_kg", "factor": 1},
        "Alanine": {"field": "alanine_total_g_kg", "factor": 1},
        "Aspartic acid": {"field": "aspartic_acid_total_g_kg", "factor": 1},
        "Glutamic acid": {"field": "glutamic_acid_total_g_kg", "factor": 1},
        "Glycine": {"field": "glycine_total_g_kg", "factor": 1},
        "Serine": {"field": "serine_total_g_kg", "factor": 1},
        "Proline": {"field": "proline_total_g_kg", "factor": 1},

        # --- 5. 豬 SID 胺基酸 ---
        "Lysine, ileal standardised, pig": {"field": "lysine_sid_pig_g_kg", "factor": 1},
        "Methionine, ileal standardised, pig": {"field": "methionine_sid_pig_g_kg", "factor": 1},
        "Methionine + cystine, ileal standardised, pig": {"field": "met_cys_sid_pig_g_kg", "factor": 1},
        "Threonine, ileal standardised, pig": {"field": "threonine_sid_pig_g_kg", "factor": 1},
        "Tryptophan, ileal standardised, pig": {"field": "tryptophan_sid_pig_g_kg", "factor": 1},
        "Valine, ileal standardised, pig": {"field": "valine_sid_pig_g_kg", "factor": 1},
        "Isoleucine, ileal standardised, pig": {"field": "isoleucine_sid_pig_g_kg", "factor": 1},
        "Leucine, ileal standardised, pig": {"field": "leucine_sid_pig_g_kg", "factor": 1},
        "Histidine, ileal standardised, pig": {"field": "histidine_sid_pig_g_kg", "factor": 1},
        "Arginine, ileal standardised, pig": {"field": "arginine_sid_pig_g_kg", "factor": 1},

        # --- 6. 脂肪酸 ---
        "C18:2 linoleic acid": {"field": "linoleic_acid_g_kg", "factor": 1},
        "C18:3 linolenic acid": {"field": "linolenic_acid_g_kg", "factor": 1},

        # --- 7. 維生素 ---
        "Vitamin A": {"field": "vitamin_a_kiu_kg", "factor": 1},
        "Vitamin D": {"field": "vitamin_d_kiu_kg", "factor": 1},
        "Vitamin E": {"field": "vitamin_e_mg_kg", "factor": 1},
        "Vitamin K": {"field": "vitamin_k_mg_kg", "factor": 1},
        "Choline": {"field": "choline_mg_kg", "factor": 1}, 
        "Vitamin B2 riboflavin": {"field": "riboflavin_mg_kg", "factor": 1},
        "Niacin": {"field": "niacin_mg_kg", "factor": 1},
        "Pantothenic acid": {"field": "pantothenic_acid_mg_kg", "factor": 1},
        "Vitamin B12": {"field": "vitamin_b12_ug_kg", "factor": 1}, 
        "Folic acid": {"field": "folic_acid_mg_kg", "factor": 1},

        # --- 8. 碳水化合物與纖維 ---
        "Water insoluble cell walls": {"field": "tdf_percent", "factor": 1},

        # --- 9. 家禽 SID 胺基酸 (Poultry SID) ---
        "Lysine, ileal standardized, poultry": {"field": "lysine_sid_poultry_g_kg", "factor": 1},
        "Methionine, ileal standardized, poultry": {"field": "methionine_sid_poultry_g_kg", "factor": 1},
        "Cystine, ileal standardized, poultry": {"field": "cystine_sid_poultry_g_kg", "factor": 1},
        "Methionine + cystine, ileal standardized, poultry": {"field": "met_cys_sid_poultry_g_kg", "factor": 1},
        "Threonine, ileal standardized, poultry": {"field": "threonine_sid_poultry_g_kg", "factor": 1},
        "Tryptophan, ileal standardized, poultry": {"field": "tryptophan_sid_poultry_g_kg", "factor": 1},
        "Valine, ileal standardized, poultry": {"field": "valine_sid_poultry_g_kg", "factor": 1},
        "Isoleucine, ileal standardized, poultry": {"field": "isoleucine_sid_poultry_g_kg", "factor": 1},
        "Leucine, ileal standardized, poultry": {"field": "leucine_sid_poultry_g_kg", "factor": 1},
        "Phenylalanine, ileal standardized, poultry": {"field": "phenylalanine_sid_poultry_g_kg", "factor": 1},
        "Tyrosine, ileal standardized, poultry": {"field": "tyrosine_sid_poultry_g_kg", "factor": 1},
        "Phenylalanine + tyrosine, ileal standardized, poultry": {"field": "phe_tyr_sid_poultry_g_kg", "factor": 1},
        "Histidine, ileal standardized, poultry": {"field": "histidine_sid_poultry_g_kg", "factor": 1},
        "Arginine, ileal standardized, poultry": {"field": "arginine_sid_poultry_g_kg", "factor": 1},
        "Alanine, ileal standardized, poultry": {"field": "alanine_sid_poultry_g_kg", "factor": 1},
        "Aspartic acid, ileal standardized, poultry": {"field": "aspartic_acid_sid_poultry_g_kg", "factor": 1},
        "Glutamic acid, ileal standardized, poultry": {"field": "glutamic_acid_sid_poultry_g_kg", "factor": 1},
        "Glycine, ileal standardized, poultry": {"field": "glycine_sid_poultry_g_kg", "factor": 1},
        "Serine, ileal standardized, poultry": {"field": "serine_sid_poultry_g_kg", "factor": 1},
        "Proline, ileal standardized, poultry": {"field": "proline_sid_poultry_g_kg", "factor": 1},
    }

    def guess_category(self, name):
        """根據原料名稱猜測分類"""
        n = name.lower()
        if any(x in n for x in ['maize', 'wheat', 'barley', 'rice', 'oat', 'sorghum', 'bran']):
            return 'CEREAL' # 對應 choices: CEREAL
        if any(x in n for x in ['soybean', 'canola', 'rapeseed', 'meal', 'gluten', 'peanut']):
            return 'OIL_SEED' # 對應 choices: OIL_SEED (含蛋白粕)
        if any(x in n for x in ['bean', 'pea', 'lupin']):
            return 'LEGUME'
        if any(x in n for x in ['cassava', 'potato', 'beet']):
            return 'TUBER'
        if any(x in n for x in ['oil', 'fat', 'tallow', 'lard']):
            return 'OIL_FAT'
        if any(x in n for x in ['phosphate', 'limestone', 'calcium', 'salt']):
            return 'MINERAL'
        if any(x in n for x in ['lysine', 'methionine', 'threonine']):
            return 'ADDITIVE'
        if any(x in n for x in ['fish', 'shrimp', 'squid', 'meat', 'blood']):
            return 'FISH_MARINE' # 或 ANIMAL_TERRESTRIAL (這裡簡單歸類)
        return 'OTHER'

    def get_parameter_ids(self, soup):
        """解析下拉選單取得參數 ID"""
        options = {}
        select_name = ""
        found_select = None
        all_selects = soup.find_all('select')
        
        for select in all_selects:
            option_texts = [opt.get_text().strip() for opt in select.find_all('option')]
            if "Crude protein" in option_texts or "Dry matter" in option_texts:
                found_select = select
                break
        
        if found_select:
            select_name = found_select.get('name')
            for opt in found_select.find_all('option'):
                val = opt.get('value')
                text = opt.get_text().strip()
                if val and val.lower() != 'all' and val != '':
                    options[text] = val
            return options, select_name
        return {}, ""

    def translate_text(self, text):
        """翻譯英文名稱並進行術語修正"""
        try:
            translated = self.translator.translate(text)
            for eng_term, fix_term in self.TERM_FIXES.items():
                if eng_term.lower() in text.lower():
                    if "Meal" in eng_term and "餐" in translated:
                        translated = translated.replace("餐", "粕")
            return translated
        except Exception as e:
            return text

    def handle(self, *args, **options):
        self.stdout.write("--- 開始執行 FeedTables 爬蟲 ---")

        # 1. 初始化記憶體資料庫
        feed_database = {}

        # 2. 取得網站參數列表
        self.stdout.write("正在取得參數 ID 列表...")
        try:
            response = requests.get(self.PROFILE_URL, headers=self.HEADERS)
            soup = BeautifulSoup(response.text, 'html.parser')
            site_param_map, param_input_name = self.get_parameter_ids(soup)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"無法連線至網站: {e}"))
            return

        if not site_param_map:
            self.stdout.write(self.style.ERROR("找不到參數下拉選單，網站結構可能已變更。"))
            return

        # 3. 迴圈抓取各項參數
        total_fields = len(self.FIELD_MAPPING)
        current_idx = 0

        for site_param_name, config in self.FIELD_MAPPING.items():
            current_idx += 1
            
            if site_param_name not in site_param_map:
                self.stdout.write(self.style.WARNING(f"[{current_idx}/{total_fields}] 跳過: 網站無參數 '{site_param_name}'"))
                continue

            param_id = site_param_map[site_param_name]
            target_field = config['field']
            factor = config['factor']

            self.stdout.write(f"[{current_idx}/{total_fields}] 正在抓取: {site_param_name} -> {target_field}")

            try:
                params = {
                    param_input_name: param_id,
                    'op': 'Go'
                }
                res = requests.get(self.PROFILE_URL, params=params, headers=self.HEADERS)
                
                dfs = pd.read_html(io.StringIO(res.text))
                if dfs:
                    df = max(dfs, key=len)
                    df.columns = [c.strip() for c in df.columns]
                    
                    if 'Feed' in df.columns and 'As fed' in df.columns:
                        for _, row in df.iterrows():
                            feed_name = row['Feed']
                            raw_val = row['As fed']

                            if feed_name not in feed_database:
                                feed_database[feed_name] = {}

                            try:
                                val_str = str(raw_val).replace('<', '').replace('>', '').strip()
                                val = float(val_str)
                                feed_database[feed_name][target_field] = round(val * factor, 4)
                            except ValueError:
                                pass
                
                time.sleep(0.5) # 禮貌性延遲

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"抓取參數 {site_param_name} 時發生錯誤: {e}"))
        
        # 4. 匯出 CSV 預覽
        self.stdout.write("--- 正在產生前 10 筆資料的 CSV 預覽 ---")
        preview_data = []
        preview_items = list(feed_database.items())[:10]
        
        for name, data in preview_items:
            row = data.copy()
            row['name'] = name
            preview_data.append(row)
            
        if preview_data:
            df_preview = pd.DataFrame(preview_data)
            cols = ['name'] + [c for c in df_preview.columns if c != 'name']
            df_preview = df_preview[cols]
            csv_filename = 'crawled_data_preview.csv'
            df_preview.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            self.stdout.write(self.style.SUCCESS(f"已輸出 CSV 檔案: {csv_filename}"))

        # 5. 翻譯與寫入資料庫
        total_items = len(feed_database)
        self.stdout.write(f"--- 抓取完成 (共 {total_items} 筆)，開始翻譯並寫入資料庫 ---")
        self.stdout.write("注意：翻譯過程需要呼叫 API，速度會比單純寫入慢...")

        updated_count = 0
        created_count = 0
        process_idx = 0

        for feed_name_eng, data in feed_database.items():
            process_idx += 1

            # 執行翻譯
            name_cht = self.translate_text(feed_name_eng)
            final_name = f"{name_cht} ({feed_name_eng})"

            # 每 5 筆顯示一次翻譯進度
            if process_idx % 5 == 0:
                self.stdout.write(f"[{process_idx}/{total_items}] 處理中: {final_name}")

            # 準備寫入
            defaults = data.copy()
            defaults['category'] = self.guess_category(feed_name_eng)
            defaults['share_with_org'] = False

            obj, created = Ingredient.objects.update_or_create(
                name=final_name,
                defaults=defaults
            )

            if created:
                created_count += 1
            else:
                updated_count += 1
                
        self.stdout.write(self.style.SUCCESS(f"作業完成！新增: {created_count}, 更新: {updated_count}"))
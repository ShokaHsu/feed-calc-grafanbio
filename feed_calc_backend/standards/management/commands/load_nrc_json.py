import json
import os
from django.core.management.base import BaseCommand
from standards.models import NutrientStandard

class Command(BaseCommand):
    help = '除錯版：匯入營養標準'

    def handle(self, *args, **kwargs):
        # Resolve path relative to this file so it works regardless of CWD
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        file_path = os.path.join(BASE_DIR, "nrc_standards.json")

        # 1. 印出目前位置與檔案絕對路徑
        current_dir = os.getcwd()
        abs_path = os.path.abspath(file_path)
        
        self.stdout.write(self.style.WARNING(f"--- 除錯資訊 ---"))
        self.stdout.write(f"目前工作目錄 (CWD): {current_dir}")
        self.stdout.write(f"預期讀取檔案路徑: {abs_path}")

        # 2. 檢查檔案是否存在
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"[ERROR] File not found: {file_path}"))
            # 嘗試列出目錄下所有檔案，幫你找找看
            files = os.listdir(current_dir)
            self.stdout.write(f"目錄下的檔案有: {files}")
            return

        try:
            # 3. 讀取並檢查內容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.stdout.write(f"[OK] File read, length: {len(content)} chars")

                if len(content.strip()) == 0:
                    self.stdout.write(self.style.ERROR("[ERROR] File is empty."))
                    return

                data_list = json.loads(content)
                self.stdout.write(f"[OK] JSON parsed, {len(data_list)} records to process")

            # Build the set of valid field names from the model
            valid_fields = {f.name for f in NutrientStandard._meta.get_fields() if hasattr(f, 'column')}

            # 4. 開始寫入資料庫
            count = 0
            for i, data in enumerate(data_list):
                name = data.get('name', '未知名稱')
                safe_name = str(name).encode('ascii', errors='replace').decode('ascii')
                self.stdout.write(f"[{i+1}] Writing: {safe_name} ...", ending='')

                try:
                    # Strip //_* comment keys, rename comment→description, drop unknown fields
                    filtered = {}
                    for key, value in data.items():
                        if key.startswith('//_'):
                            continue
                        if key == 'comment':
                            filtered['description'] = value
                        elif key in valid_fields:
                            filtered[key] = value

                    obj, created = NutrientStandard.objects.update_or_create(
                        name=name,
                        defaults={
                            **filtered,
                            "is_public": True,
                            "created_by": None
                        }
                    )
                    status = "新增" if created else "更新"
                    self.stdout.write(self.style.SUCCESS(f" -> {status}成功"))
                    count += 1
                except Exception as db_err:
                    self.stdout.write(self.style.ERROR(f" -> 失敗: {db_err}"))

            self.stdout.write(self.style.SUCCESS(f"--- 結束 ---"))
            self.stdout.write(self.style.SUCCESS(f"共成功寫入 {count} 筆資料。"))
            
        except json.JSONDecodeError as json_err:
            self.stdout.write(self.style.ERROR(f"[ERROR] JSON decode error: {json_err}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[ERROR] Unexpected error: {str(e)}"))
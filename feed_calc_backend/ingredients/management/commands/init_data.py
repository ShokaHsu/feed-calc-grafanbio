from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings

class Command(BaseCommand):
    help = '初始化所有資料 (NRC 標準 + 爬蟲原料)'

    def handle(self, *args, **options):
        self.stdout.write("1. 開始匯入 NRC 標準...")
        try:
            call_command('load_nrc_json')
            self.stdout.write(self.style.SUCCESS("   NRC 標準匯入成功"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   NRC 匯入失敗: {e}"))

        self.stdout.write("\n2. 開始執行原料爬蟲...")
        try:
            call_command('crawl_ingredients')
            self.stdout.write(self.style.SUCCESS("   爬蟲執行完成"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   爬蟲失敗: {e}"))
            
        self.stdout.write(self.style.SUCCESS("\n初始化流程結束"))

        db_settings = settings.DATABASES['default']
        print("--------------------------------------------------")
        print(f"DEBUG: Connecting to Engine: {db_settings['ENGINE']}")
        print(f"DEBUG: Database Name: {db_settings['NAME']}")
        print(f"DEBUG: Database Host: {db_settings.get('HOST', 'Local File')}")
        print("--------------------------------------------------")
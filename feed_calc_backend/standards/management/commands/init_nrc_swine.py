from django.core.management.base import BaseCommand
from standards.models import NutrientStandard

class Command(BaseCommand):
    help = '初始化 NRC 2012 豬隻營養標準'

    def handle(self, *args, **kwargs):
        # 定義 NRC 標準數據 (參考值)
        # 單位注意：CP(%), ME(kcal/kg), 氨基酸/礦物質(g/kg)
        standards_data = [
            {
                "name": "保育前期 (7-11 kg) - NRC 2012",
                "species": "SWINE",
                "stage": "NURSERY",
                "description": "高營養需求，強調消化率與氨基酸平衡。",
                # 能量
                "min_me_pig_kcal_per_kg": 3265,
                # 主要成分
                "min_crude_protein_percent": 20.0,
                # SID 胺基酸 (NRC 2012 建議使用 SID)
                "min_lysine_sid_pig_g_kg": 13.5,    # 1.35%
                "min_methionine_sid_pig_g_kg": 3.8, # 0.38%
                "min_met_cys_sid_pig_g_kg": 7.8,    # 0.78%
                "min_threonine_sid_pig_g_kg": 8.5,  # 0.85%
                # 礦物質
                "min_calcium_g_per_kg": 8.0,        # 0.80%
                "min_available_phosphorus_g_per_kg": 4.0, # 0.40%
            },
            {
                "name": "保育後期 (11-25 kg) - NRC 2012",
                "species": "SWINE",
                "stage": "NURSERY",
                "description": "過渡到固態飼料，降低腹瀉風險。",
                # 能量
                "min_me_pig_kcal_per_kg": 3265,
                # 主要成分
                "min_crude_protein_percent": 18.0,
                # SID 胺基酸
                "min_lysine_sid_pig_g_kg": 12.3,    # 1.23%
                "min_methionine_sid_pig_g_kg": 3.4,
                "min_met_cys_sid_pig_g_kg": 7.1,
                "min_threonine_sid_pig_g_kg": 7.6,
                # 礦物質
                "min_calcium_g_per_kg": 7.0,
                "min_available_phosphorus_g_per_kg": 3.2,
            },
            {
                "name": "生長豬 (25-50 kg) - NRC 2012",
                "species": "SWINE",
                "stage": "GROWER",
                "description": "骨骼與肌肉快速發育期。",
                # 能量
                "min_me_pig_kcal_per_kg": 3265,
                # 主要成分
                "min_crude_protein_percent": 16.0,
                # SID 胺基酸
                "min_lysine_sid_pig_g_kg": 9.8,     # 0.98%
                "min_methionine_sid_pig_g_kg": 2.7,
                "min_met_cys_sid_pig_g_kg": 5.7,
                "min_threonine_sid_pig_g_kg": 6.1,
                # 礦物質
                "min_calcium_g_per_kg": 6.0,
                "min_available_phosphorus_g_per_kg": 2.8,
            },
            {
                "name": "肥育前期 (50-75 kg) - NRC 2012",
                "species": "SWINE",
                "stage": "FINISHER",
                "description": "主要堆積瘦肉。",
                # 能量
                "min_me_pig_kcal_per_kg": 3265,
                # 主要成分
                "min_crude_protein_percent": 14.5,
                # SID 胺基酸
                "min_lysine_sid_pig_g_kg": 8.5,     # 0.85%
                "min_methionine_sid_pig_g_kg": 2.4,
                "min_met_cys_sid_pig_g_kg": 5.0,
                "min_threonine_sid_pig_g_kg": 5.4,
                # 礦物質
                "min_calcium_g_per_kg": 5.5,
                "min_available_phosphorus_g_per_kg": 2.5,
            },
            {
                "name": "肥育後期 (75-100 kg) - NRC 2012",
                "species": "SWINE",
                "stage": "FINISHER",
                "description": "上市前飼養，注重成本控制。",
                # 能量
                "min_me_pig_kcal_per_kg": 3265,
                # 主要成分
                "min_crude_protein_percent": 13.5,
                # SID 胺基酸
                "min_lysine_sid_pig_g_kg": 7.3,     # 0.73%
                "min_methionine_sid_pig_g_kg": 2.1,
                "min_met_cys_sid_pig_g_kg": 4.5,
                "min_threonine_sid_pig_g_kg": 4.8,
                # 礦物質
                "min_calcium_g_per_kg": 5.0,
                "min_available_phosphorus_g_per_kg": 2.3,
            },
            {
                "name": "泌乳母豬 (Lactation) - NRC 2012",
                "species": "SWINE",
                "stage": "LACTATION",
                "description": "極高能量與氨基酸需求以維持乳量。",
                # 能量
                "min_me_pig_kcal_per_kg": 3300,
                # 主要成分
                "min_crude_protein_percent": 17.5,
                # SID 胺基酸
                "min_lysine_sid_pig_g_kg": 10.5,    # 1.05%
                # 礦物質
                "min_calcium_g_per_kg": 8.5,
                "min_available_phosphorus_g_per_kg": 4.0,
            },
            {
                "name": "懷孕母豬 (Gestation) - NRC 2012",
                "species": "SWINE",
                "stage": "GESTATION",
                "description": "維持體態與胎兒發育。",
                # 能量
                "min_me_pig_kcal_per_kg": 3100,
                # 主要成分
                "min_crude_protein_percent": 12.5,
                # SID 胺基酸
                "min_lysine_sid_pig_g_kg": 6.0,     # 0.60%
                # 礦物質
                "min_calcium_g_per_kg": 7.5,
                "min_available_phosphorus_g_per_kg": 3.5,
            },
        ]

        count = 0
        for data in standards_data:
            # 使用 update_or_create 防止重複匯入
            obj, created = NutrientStandard.objects.update_or_create(
                name=data['name'], # 以名稱當作唯一識別
                defaults={
                    **data,
                    "is_public": True,   # 設定為公用
                    "created_by": None   # 系統建立
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'新增標準: {obj.name}'))
                count += 1
            else:
                self.stdout.write(f'更新標準: {obj.name}')

        self.stdout.write(self.style.SUCCESS(f'完成！共處理 {len(standards_data)} 筆資料，新增 {count} 筆。'))
from django.db import models
from django.conf import settings
from common.models import TimeStampedModel

class NutrientStandard(TimeStampedModel):
    """
    營養標準表 (配合 FeedTables 參數擴充)
    """
    SPECIES_CHOICES = (('SWINE', '豬'), ('POULTRY', '家禽'), ('RUMINANT', '反芻'), ('AQUA', '水產'), ('OTHER', '其他'))
    # (STAGE_CHOICES 省略，請保留原本的內容)
    # 生長階段選項 (做成代碼，前端顯示中文)
    STAGE_CHOICES = (
        # --- 豬 ---
        ('NURSERY', '保育期 (Nursery)'),
        ('GROWER', '生長期 (Grower)'),
        ('FINISHER', '肥育期 (Finisher)'),
        ('GESTATION', '懷孕期 (Gestation)'),
        ('LACTATION', '泌乳期 (Lactation)'),
        
        # --- 家禽 ---
        ('BROILER_STARTER', '肉雞-前期 (Starter)'),
        ('BROILER_GROWER', '肉雞-中期 (Grower)'),
        ('BROILER_FINISHER', '肉雞-後期 (Finisher)'),
        ('LAYER_CHICK', '蛋雞-育雛 (Chick)'),
        ('LAYER_PULLET', '蛋雞-中雞 (Pullet)'),
        ('LAYER_LAYING', '蛋雞-產蛋 (Laying)'),

        # --- ✨ 反芻 (Ruminant) ---
        ('LACTATION_COW_HP', '高泌乳牛 (Lactating Ruminants)'),
        ('LACTATION_COW_LP', '低泌乳牛 (Lactating Ruminants)'),
        ('DRY_COW', '乾乳牛 (Dry Cow)'),
        ('BEEF_CATTLE', '肉牛 (Beef Cattle)'),
        ('HEIFER', '女牛 (Heifer)'),

        # --- ✨ 水產 (Aqua) ---
        ('CARNIVOROUS_FISH', '肉食性魚類 (Carnivorous)'),
        ('HERBIVOROUS_FISH', '草食性魚類 (Herbivorous)'),
        ('SHRIMP', '蝦類 (Shrimp)'),

        # --- 其他 ---
        ('OTHER', '其他階段'),
    )


    name = models.CharField(max_length=100, verbose_name="標準名稱")
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES, verbose_name="物種")
    stage = models.CharField(max_length=30, choices=STAGE_CHOICES, default='OTHER', verbose_name="生長階段")
    description = models.TextField(blank=True, null=True, verbose_name="備註說明")

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='custom_standards')
    is_public = models.BooleanField(default=False, verbose_name="是否為公用")

    # ==========================================
    # 1. 主要成分限制 (Main Constituents)
    # ==========================================
    min_crude_protein_percent = models.FloatField(verbose_name="CP Min (%)", null=True, blank=True)
    max_crude_protein_percent = models.FloatField(verbose_name="CP Max (%)", null=True, blank=True)
    max_crude_fiber_percent = models.FloatField(verbose_name="Fiber Max (%)", null=True, blank=True)
    max_crude_fat_percent = models.FloatField(verbose_name="Fat Max (%)", null=True, blank=True)
    min_dm_percent = models.FloatField(verbose_name="DM Min (%)", null=True, blank=True)

    # ==========================================
    # 2. 能量限制 (Energy)
    # ==========================================
    # 豬
    min_de_pig_kcal_per_kg = models.FloatField(null=True, blank=True, verbose_name="DE Pig Min")
    min_me_pig_kcal_per_kg = models.FloatField(null=True, blank=True, verbose_name="ME Pig Min")
    min_ne_pig_growth_kcal_per_kg = models.FloatField(null=True, blank=True, verbose_name="NE Growth Min")
    min_ne_pig_sow_kcal_per_kg = models.FloatField(null=True, blank=True, verbose_name="NE Sow Min")
    # 家禽
    min_me_broiler_kcal_per_kg = models.FloatField(null=True, blank=True, verbose_name="ME Broiler Min")
    min_me_layer_kcal_per_kg = models.FloatField(null=True, blank=True, verbose_name="ME Layer Min")

    # ==========================================
    # 3. 總胺基酸限制 (Total AA)
    # ==========================================
    min_lysine_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="Total Lys Min")
    min_methionine_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="Total Met Min")
    min_met_cys_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="Total M+C Min")
    min_threonine_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="Total Thr Min")
    min_tryptophan_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="Total Trp Min")

    # ==========================================
    # 4. SID 胺基酸限制 (SID AA - Pig)
    # ==========================================
    min_lysine_sid_pig_g_kg = models.FloatField(null=True, blank=True, verbose_name="SID Lys Min")
    min_methionine_sid_pig_g_kg = models.FloatField(null=True, blank=True, verbose_name="SID Met Min")
    min_met_cys_sid_pig_g_kg = models.FloatField(null=True, blank=True, verbose_name="SID M+C Min")
    min_threonine_sid_pig_g_kg = models.FloatField(null=True, blank=True, verbose_name="SID Thr Min")
    min_tryptophan_sid_pig_g_kg = models.FloatField(null=True, blank=True, verbose_name="SID Trp Min")

    # ==========================================
    # 4-1. SID 胺基酸限制 (SID AA - Broiler)
    # ==========================================
    min_lysine_sid_broiler_g_kg = models.FloatField(null=True, blank=True, verbose_name="SID Lys Min_broiler")
    min_methionine_sid_broiler_g_kg = models.FloatField(null=True, blank=True, verbose_name="SID Met Min_broiler")
    min_met_cys_sid_broiler_g_kg = models.FloatField(null=True, blank=True, verbose_name="SID M+C Min_broiler")
    min_threonine_sid_broiler_g_kg = models.FloatField(null=True, blank=True, verbose_name="SID Thr Min_broiler")
    min_tryptophan_sid_broiler_g_kg = models.FloatField(null=True, blank=True, verbose_name="SID Trp Min_broiler")
    
    # ==========================================
    # 5. 礦物質限制 (Minerals)
    # ==========================================
    min_calcium_g_per_kg = models.FloatField(verbose_name="Ca Min", null=True, blank=True)
    max_calcium_g_per_kg = models.FloatField(verbose_name="Ca Max", null=True, blank=True)
    min_phosphorus_g_per_kg = models.FloatField(verbose_name="Total P Min", null=True, blank=True)
    min_available_phosphorus_g_per_kg = models.FloatField(verbose_name="Avail P Min", null=True, blank=True)
    min_sodium_g_per_kg = models.FloatField(verbose_name="Na Min", null=True, blank=True)

    class Meta:
        ordering = ['species', 'stage', 'name']

    def __str__(self):
        return f"[{self.get_species_display()}-{self.get_stage_display()}] {self.name}"
from django.db import models
from django.conf import settings

# ==========================================
# 1. 原料分類 (參考 FeedTables)
# ==========================================
CATEGORY_CHOICES = (
    ('CEREAL', '穀物 (Cereal)'),
    ('OIL_SEED', '油籽類 (Oil Seed)'),
    ('LEGUME', '豆類 (Legume)'),
    ('PROTEIN', '蛋白質飼料 (Protein Feed)'),
    ('ENERGY', '能量飼料 (Energy Feed)'),
    ('OIL_FAT', '油脂 (Oil/Fat)'),
    ('TUBER', '塊根塊莖 (Tuber/Root)'),
    ('FORAGE', '牧草 (Forages/roughages)'),
    ('FISH_MARINE', '魚類/海洋 (Fish/Marine)'),
    ('ANIMAL_TERRESTRIAL', '陸生動物產品 (Animal products)'),
    ('DAIRY', '乳製品 (Dairy products)'),
    ('MINERAL', '礦物質/維他命 (Mineral/Vitamins)'),
    ('ADDITIVE', '添加劑 (Additives)'),
    ('AMINO_ACID', '合成氨基酸 (Amino acids)'),
    ('OTHER', '其他 (Other)'),
)
                      
class Ingredient(models.Model):
    # --- 基本資訊 ---
    name = models.CharField(max_length=120, db_index=True, verbose_name="原料名稱")
    category = models.CharField(
        max_length=30, 
        choices=CATEGORY_CHOICES, 
        default='OTHER', 
        verbose_name="分類"
    )
    cost_per_kg_twd = models.FloatField(default=0, verbose_name="成本 (TWD/kg)")
    
    # 權限設定
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='custom_ingredients'
    )
    is_public = models.BooleanField(default=False, verbose_name="是否為公用")
    share_with_org = models.BooleanField(default=False, verbose_name="分享給企業成員")

    # ==========================================
    # 2. 主要成分 (Main Constituents)
    # 單位: % (As Fed)
    # ==========================================
    dm_percent = models.FloatField(null=True, blank=True, verbose_name="乾物質 (DM%)")
    crude_protein_percent = models.FloatField(null=True, blank=True, verbose_name="粗蛋白 (CP%)")
    crude_fiber_percent = models.FloatField(null=True, blank=True, verbose_name="粗纖維 (CF%)")
    crude_fat_percent = models.FloatField(null=True, blank=True, verbose_name="粗脂肪 (EE%)")
    ash_percent = models.FloatField(null=True, blank=True, verbose_name="粗灰分 (Ash%)")
    starch_percent = models.FloatField(null=True, blank=True, verbose_name="澱粉 (Starch%)")
    sugar_percent = models.FloatField(null=True, blank=True, verbose_name="糖 (Sugar%)")
    ndf_percent = models.FloatField(null=True, blank=True, verbose_name="中洗纖維 (NDF%)")
    adf_percent = models.FloatField(null=True, blank=True, verbose_name="酸洗纖維 (ADF%)")

    # ==========================================
    # 3. 能量 (Energy)
    # 單位: kcal/kg
    # ==========================================
    # 豬
    de_pig_kcal_per_kg = models.FloatField(null=True, blank=True, verbose_name="豬消化能 (DE Pig)")
    me_pig_kcal_per_kg = models.FloatField(null=True, blank=True, verbose_name="豬代謝能 (ME Pig)")
    ne_pig_growth_kcal_per_kg = models.FloatField(null=True, blank=True, verbose_name="肉豬淨能 (NE Growth)")
    ne_pig_sow_kcal_per_kg = models.FloatField(null=True, blank=True, verbose_name="母豬淨能 (NE Sow)")
    
    # 家禽
    
    amen_broiler_kcal_per_kg = models.FloatField(null=True, blank=True, verbose_name="肉雞代謝能 (AMEn Broiler)")
    amen_cockerel_kcal_per_kg = models.FloatField(null=True, blank=True, verbose_name="公雞/蛋雞代謝能 (AMEn Cockerel)")

    # 反芻動物
    tdn_percent = models.FloatField(null=True, blank=True, verbose_name="總可消化養分 (TDN%)")
    me_ruminant_kcal_per_kg = models.FloatField(null=True, blank=True, verbose_name="反芻代謝能 (ME Ruminant)")
    ne_ruminant_kcal_per_kg = models.FloatField(null=True, blank=True, verbose_name="反芻淨能 (NE kcal/kg)")

    # ==========================================
    # 4. 礦物質 (Minerals)
    # 單位: g/kg (常量), mg/kg (微量)
    # ==========================================
    # 常量元素 (g/kg)
    calcium_g_per_kg = models.FloatField(null=True, blank=True, verbose_name="鈣 (Ca)")
    phosphorus_g_per_kg = models.FloatField(null=True, blank=True, verbose_name="總磷 (P)")
    phytate_P_g_per_kg = models.FloatField(null=True, blank=True, verbose_name="植酸磷 (P)")
    sodium_g_per_kg = models.FloatField(null=True, blank=True, verbose_name="鈉 (Na)")
    chloride_g_per_kg = models.FloatField(null=True, blank=True, verbose_name="氯 (Cl)")
    potassium_g_per_kg = models.FloatField(null=True, blank=True, verbose_name="鉀 (K)")
    magnesium_g_per_kg = models.FloatField(null=True, blank=True, verbose_name="鎂 (Mg)")
    
    # 微量元素 (mg/kg)
    iron_mg_per_kg = models.FloatField(null=True, blank=True, verbose_name="鐵 (Fe)")
    copper_mg_per_kg = models.FloatField(null=True, blank=True, verbose_name="銅 (Cu)")
    manganese_mg_per_kg = models.FloatField(null=True, blank=True, verbose_name="錳 (Mn)")
    zinc_mg_per_kg = models.FloatField(null=True, blank=True, verbose_name="鋅 (Zn)")
    selenium_mg_per_kg = models.FloatField(null=True, blank=True, verbose_name="硒 (Se)")

    # 豬 (Pig) - 消化磷 (Digestible P)
    digestible_p_pig_no_phytase_g_kg = models.FloatField(null=True, blank=True, verbose_name="豬消化磷 (無植酸酶) DP Pig (no phyt.)")
    digestible_p_pig_with_phytase_g_kg = models.FloatField(null=True, blank=True, verbose_name="豬消化磷 (含植酸酶) DP Pig (w. phyt.)")
    
    # 家禽 (Poultry) - 有效磷 (Available P)
    available_p_cockerel_g_kg = models.FloatField(null=True, blank=True, verbose_name="公雞有效磷 Avail. P Cockerel")
    available_p_broiler_g_kg = models.FloatField(null=True, blank=True, verbose_name="肉雞有效磷 Avail. P Broiler")

    # ==========================================
    # 5. 胺基酸 (Amino Acids) - 總量 (Total)
    # 單位: g/kg
    # ==========================================
    lysine_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="總離胺酸 (Lys)")
    methionine_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="總蛋胺酸 (Met)")
    cystine_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="總胱胺酸 (Cys)")
    met_cys_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="總含硫胺基酸 (M+C)")
    threonine_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="總羥丁胺酸 (Thr)")
    tryptophan_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="總色胺酸 (Trp)")
    valine_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="總纈胺酸 (Val)")
    isoleucine_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="總異白胺酸 (Ile)")
    leucine_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="總白胺酸 (Leu)")
    phenylalanine_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="總苯丙胺酸 (Phe)")
    tyrosine_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="總酪胺酸 (Tyr)")
    histidine_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="總組胺酸 (His)")
    arginine_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="總精胺酸 (Arg)")
    alanine_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="總丙胺酸 (Ala)")
    aspartic_acid_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="總天門冬胺酸 (Asp)")
    glutamic_acid_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="總麩胺酸 (Glu)")
    glycine_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="總甘胺酸 (Gly)")
    serine_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="總絲胺酸 (Ser)")
    proline_total_g_kg = models.FloatField(null=True, blank=True, verbose_name="總脯胺酸 (Pro)")

    # ==========================================
    # 6. 胺基酸 (Amino Acids) - 豬迴腸消化 (SID Pig)
    # 單位: g/kg (Standardized Ileal Digestible)
    # ==========================================
    lysine_sid_pig_g_kg = models.FloatField(null=True, blank=True, verbose_name="SID 離胺酸 (Lys)")
    methionine_sid_pig_g_kg = models.FloatField(null=True, blank=True, verbose_name="SID 蛋胺酸 (Met)")
    met_cys_sid_pig_g_kg = models.FloatField(null=True, blank=True, verbose_name="SID M+C")
    threonine_sid_pig_g_kg = models.FloatField(null=True, blank=True, verbose_name="SID 羥丁胺酸 (Thr)")
    tryptophan_sid_pig_g_kg = models.FloatField(null=True, blank=True, verbose_name="SID 色胺酸 (Trp)")
    valine_sid_pig_g_kg = models.FloatField(null=True, blank=True, verbose_name="SID 纈胺酸 (Val)")
    isoleucine_sid_pig_g_kg = models.FloatField(null=True, blank=True, verbose_name="SID 異白胺酸 (Ile)")
    leucine_sid_pig_g_kg = models.FloatField(null=True, blank=True, verbose_name="SID 白胺酸 (Leu)")
    histidine_sid_pig_g_kg = models.FloatField(null=True, blank=True, verbose_name="SID 組胺酸 (His)")
    arginine_sid_pig_g_kg = models.FloatField(null=True, blank=True, verbose_name="SID 精胺酸 (Arg)")

    # ==========================================
    # 7. 脂肪酸 (Fatty Acids)
    # 單位: g/kg
    # ==========================================
    linoleic_acid_g_kg = models.FloatField(null=True, blank=True, verbose_name="亞麻油酸 (C18:2)")
    linolenic_acid_g_kg = models.FloatField(null=True, blank=True, verbose_name="次亞麻油酸 (C18:3)")

    # ==========================================
    # 8. 維生素 (Vitamins) - 僅列常用
    # 單位: 1000 IU/kg 或 mg/kg
    # ==========================================
    vitamin_e_mg_kg = models.FloatField(null=True, blank=True, verbose_name="維生素 E (mg/kg)")
    choline_mg_kg = models.FloatField(null=True, blank=True, verbose_name="膽鹼 (mg/kg)")
    vitamin_a_kiu_kg = models.FloatField(null=True, blank=True, verbose_name="維生素 A (1000 IU/kg)")
    vitamin_d_kiu_kg = models.FloatField(null=True, blank=True, verbose_name="維生素 D (1000 IU/kg)")
    vitamin_k_mg_kg = models.FloatField(null=True, blank=True, verbose_name="維生素 K (mg/kg)")
    riboflavin_mg_kg = models.FloatField(null=True, blank=True, verbose_name="核黃素 B2 (mg/kg)")
    niacin_mg_kg = models.FloatField(null=True, blank=True, verbose_name="菸鹼酸 B3 (mg/kg)")
    pantothenic_acid_mg_kg = models.FloatField(null=True, blank=True, verbose_name="泛酸 B5 (mg/kg)")
    vitamin_b12_ug_kg = models.FloatField(null=True, blank=True, verbose_name="維生素 B12 (ug/kg)")
    folic_acid_mg_kg = models.FloatField(null=True, blank=True, verbose_name="葉酸 B9 (mg/kg)")
    vitamin_b1_mg_kg  = models.FloatField(null=True, blank=True, verbose_name="維生素 B1 (mg/kg)")
    vitamin_b6_mg_kg  = models.FloatField(null=True, blank=True, verbose_name="維生素 B6 (mg/kg)")
    biotin_mcg_kg     = models.FloatField(null=True, blank=True, verbose_name="生物素 (mcg/kg)")

    # ==========================================
    # 11. 碳水化合物與纖維 (Carbohydrates & Fiber)
    # ==========================================
    nsp_percent = models.FloatField(null=True, blank=True, verbose_name="非澱粉多醣 (NSP%)")
    tdf_percent = models.FloatField(null=True, blank=True, verbose_name="總膳食纖維 (TDF%)")
    sol_nsp_percent = models.FloatField(null=True, blank=True, verbose_name="水溶性 NSP")
    insol_nsp_percent = models.FloatField(null=True, blank=True, verbose_name="不可溶 NSP")

    # ==========================================
    # 12. 脂肪酸品質 (Fatty Acids)
    # ==========================================
    sfa_g_kg = models.FloatField(null=True, blank=True, verbose_name="總飽和脂肪酸 (SFA)")
    ufa_g_kg = models.FloatField(null=True, blank=True, verbose_name="總不飽和脂肪酸 (UFA)")

    # ==========================================
    # 15. 家禽 SID 胺基酸 (Poultry SID / DIS Amino Acids)
    # 單位: g/kg
    # ==========================================
    lysine_sid_poultry_g_kg = models.FloatField(null=True, blank=True, verbose_name="家禽 SID 離胺酸 (Lys)")
    methionine_sid_poultry_g_kg = models.FloatField(null=True, blank=True, verbose_name="家禽 SID 蛋胺酸 (Met)")
    cystine_sid_poultry_g_kg = models.FloatField(null=True, blank=True, verbose_name="家禽 SID 胱胺酸 (Cys)")
    met_cys_sid_poultry_g_kg = models.FloatField(null=True, blank=True, verbose_name="家禽 SID M+C")
    threonine_sid_poultry_g_kg = models.FloatField(null=True, blank=True, verbose_name="家禽 SID 羥丁胺酸 (Thr)")
    tryptophan_sid_poultry_g_kg = models.FloatField(null=True, blank=True, verbose_name="家禽 SID 色胺酸 (Trp)")
    valine_sid_poultry_g_kg = models.FloatField(null=True, blank=True, verbose_name="家禽 SID 纈胺酸 (Val)")
    isoleucine_sid_poultry_g_kg = models.FloatField(null=True, blank=True, verbose_name="家禽 SID 異白胺酸 (Ile)")
    leucine_sid_poultry_g_kg = models.FloatField(null=True, blank=True, verbose_name="家禽 SID 白胺酸 (Leu)")
    phenylalanine_sid_poultry_g_kg = models.FloatField(null=True, blank=True, verbose_name="家禽 SID 苯丙胺酸 (Phe)")
    tyrosine_sid_poultry_g_kg = models.FloatField(null=True, blank=True, verbose_name="家禽 SID 酪胺酸 (Tyr)")
    phe_tyr_sid_poultry_g_kg = models.FloatField(null=True, blank=True, verbose_name="家禽 SID Phe+Tyr")
    histidine_sid_poultry_g_kg = models.FloatField(null=True, blank=True, verbose_name="家禽 SID 組胺酸 (His)")
    arginine_sid_poultry_g_kg = models.FloatField(null=True, blank=True, verbose_name="家禽 SID 精胺酸 (Arg)")
    alanine_sid_poultry_g_kg = models.FloatField(null=True, blank=True, verbose_name="家禽 SID 丙胺酸 (Ala)")
    aspartic_acid_sid_poultry_g_kg = models.FloatField(null=True, blank=True, verbose_name="家禽 SID 天門冬胺酸 (Asp)")
    glutamic_acid_sid_poultry_g_kg = models.FloatField(null=True, blank=True, verbose_name="家禽 SID 麩胺酸 (Glu)")
    glycine_sid_poultry_g_kg = models.FloatField(null=True, blank=True, verbose_name="家禽 SID 甘胺酸 (Gly)")
    serine_sid_poultry_g_kg = models.FloatField(null=True, blank=True, verbose_name="家禽 SID 絲胺酸 (Ser)")
    proline_sid_poultry_g_kg = models.FloatField(null=True, blank=True, verbose_name="家禽 SID 脯胺酸 (Pro)")



    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=['created_by', 'name'], name='unique_user_ingredient')
        ]

    def __str__(self):
        return self.name
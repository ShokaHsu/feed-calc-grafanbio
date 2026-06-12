from django.db import models
from django.conf import settings
from common.models import TimeStampedModel
from standards.models import NutrientStandard # 引入營養標準模型
from accounts.models import Customer # ✨ 引入客戶模型

class Formula(TimeStampedModel):
    """
    配方主表：儲存配方名稱、總重、總成本，以及它對應的營養標準和客戶。
    """
    name = models.CharField(max_length=100, verbose_name="配方名稱")
    description = models.TextField(blank=True, null=True, verbose_name="備註")
    
    # --- 關聯設定 ---
    
    # 關聯到營養標準 (讓配方知道自己的目標)
    standard = models.ForeignKey(
        NutrientStandard, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="採用標準"
    )
    
    # ✨ [關鍵] 關聯到客戶/牧場 (取代 farm_name 欄位)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        verbose_name="歸屬客戶/牧場"
    )
    
    # 權限
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='formulas',
        verbose_name="建立者"
    )
    
    # --- 計算快照 (Snapshot) ---
    batch_size = models.FloatField(default=0.0, verbose_name="批次重量 (kg)")
    total_cost = models.FloatField(default=0.0, verbose_name="總成本")
    cost_per_kg = models.FloatField(default=0.0, verbose_name="單價 (元/kg)")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "配方"

    def __str__(self):
        return f"{self.name} ({self.customer.name if self.customer else '無客戶'})"

class FormulaItem(models.Model):
    """
    配方原料明細：儲存特定配方中使用了哪些原料及用量。
    """
    formula = models.ForeignKey(Formula, on_delete=models.CASCADE, related_name='items')
    
    ingredient = models.ForeignKey(
        'ingredients.Ingredient', 
        on_delete=models.PROTECT, # 保護機制：避免原料被誤刪
        verbose_name="原料"
    )
    
    amount_kg = models.FloatField(verbose_name="使用量 (kg)")
    
    class Meta:
        unique_together = ('formula', 'ingredient') 
        verbose_name = "配方明細"

    def __str__(self):
        return f"{self.formula.name} - {self.ingredient.name}"
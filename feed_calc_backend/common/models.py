from django.db import models

class TimeStampedModel(models.Model):
    """
    這是一個抽象模型 (Abstract Model)。
    它不會在資料庫建立真正的 Table，
    而是讓繼承它的模型自動擁有 created_at 和 updated_at 欄位。
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        abstract = True
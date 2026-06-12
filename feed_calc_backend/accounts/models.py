from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from common.models import TimeStampedModel 

# 定義物種與規模選項 (供 Customer 使用)
SPECIES_CHOICES = (
    ('SWINE', '豬'),
    ('POULTRY', '家禽'),
    ('RUMINANT', '反芻'),
    ('AQUA', '水產'),
    ('OTHER', '其他')
)

SCALE_CHOICES = (
    ('SMALL', '小型 (< 500 頭)'),
    ('MEDIUM', '中型 (500 - 2000 頭)'),
    ('LARGE', '大型 (> 2000 頭)'),
)

# ==========================================
# 1. ✨ [新增] 組織/企業模型
# ==========================================
class Organization(TimeStampedModel):
    """
    企業用戶的組織單位。
    同一組織下的使用者 (User) 可以選擇分享原料給彼此。
    """
    name = models.CharField(max_length=100, verbose_name="企業/組織名稱", unique=True)
    tax_id = models.CharField(max_length=20, verbose_name="統一編號", blank=True, null=True)
    address = models.CharField(max_length=255, verbose_name="公司地址", blank=True, null=True)
    
    def __str__(self):
        return self.name

# ==========================================
# 2. [修改] 使用者模型 (加入等級與組織)
# ==========================================
class User(AbstractUser):
    # 會員等級選項
    TIER_CHOICES = (
        ('FREE', '免費會員 (限10筆)'),
        ('SILVER', '銀級會員 (限100筆)'),
        ('ENTERPRISE', '企業會員 (無上限/可共享)'),
    )
    
    email = models.EmailField(unique=True, verbose_name="電子郵件")
    
    # ✨ [新增] 會員等級
    tier = models.CharField(
        max_length=20, 
        choices=TIER_CHOICES, 
        default='FREE', 
        verbose_name="會員等級"
    )
    
    # ✨ [新增] 所屬組織 (僅企業會員需要設定，可為空)
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='members',
        verbose_name="所屬組織"
    )

    # 登入設定
    USERNAME_FIELD = 'email' # 使用 Email 登入
    REQUIRED_FIELDS = ['username'] # 建立 superuser 時仍需輸入 username

    def __str__(self):
        org_str = f" @ {self.organization.name}" if self.organization else ""
        return f"{self.username} ({self.get_tier_display()}){org_str}"
    

# ==========================================
# 3. 客戶/牧場模型 (維持原樣，微調顯示)
# ==========================================
class Customer(TimeStampedModel):
    """
    使用者建立的客戶（牧場）資料
    """
    name = models.CharField(max_length=255, verbose_name="客戶/牧場名稱") # 移除 unique=True，避免不同使用者的客戶同名衝突
    city = models.CharField(max_length=50, verbose_name="所在縣市", blank=True)
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES, verbose_name="主要物種", blank=True)
    scale = models.CharField(max_length=20, choices=SCALE_CHOICES, verbose_name="牧場規模", blank=True)
    contact_name = models.CharField(max_length=100, blank=True, verbose_name="聯絡人")
    phone = models.CharField(max_length=20, blank=True, verbose_name="聯絡電話")
    address = models.CharField(max_length=255, blank=True, verbose_name="地址")
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='customers',
        verbose_name="擁有者"
    )

    class Meta:
        ordering = ['name']
        verbose_name = "客戶"
        # 聯合約束：同一個擁有者底下，客戶名稱不能重複 (但不同人可以有同名客戶)
        unique_together = ('name', 'owner') 

    def __str__(self):
        return self.name

class UserPreference(models.Model):
    """
    儲存使用者的偏好設定，例如：常用原料列表
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    # 使用 JSONField 儲存 ID 列表，例如 [1, 5, 10]
    favorite_ingredients = models.JSONField(default=list, blank=True)
    # ✨ [新增] 養分顯示模式 (basic / advanced)
    nutrient_display_mode = models.CharField(max_length=10, default='basic', blank=True)

    def __str__(self):
        return f"{self.user.username} 的偏好"
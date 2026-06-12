from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Customer, Organization

# 1. 註冊 Organization
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'tax_id', 'created_at')
    search_fields = ('name', 'tax_id')

# 2. 修改 UserAdmin 以顯示等級與組織
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    自訂使用者管理介面
    """
    # 1. 在列表頁顯示的欄位
    # username: 帳號
    # email: 電子郵件 (方便你檢查是否有重複)
    # is_staff: 是否為管理員
    # date_joined: 註冊時間
    # last_login: 最後登入時間 (可看出活躍度)
    list_display = ('username', 'email', 'tier', 'organization', 'is_staff', 'date_joined', 'last_login')

    # 篩選器加入 tier
    list_filter = ('tier', 'organization', 'is_staff', 'is_active')
    
    # 編輯頁面加入這些新欄位
    fieldsets = UserAdmin.fieldsets + (
        ('會員權限設定', {'fields': ('tier', 'organization')}),
    )

    # last_login 和 date_joined 通常由系統自動維護，不建議手動改
    readonly_fields = ('last_login', 'date_joined')
    
    # 3. 右側篩選器
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    
    # 4. 搜尋框 (支援搜尋帳號和 Email)
    search_fields = ('username', 'email')
    
    # 5. 預設排序 (最新的註冊在最上面)
    ordering = ('-date_joined',)

    # 如果你未來有在 User model 新增自訂欄位 (例如 'phone'), 
    # 需要修改 fieldsets 才能在編輯頁面看到，目前維持預設即可。


# 3. Customer Admin (維持原樣)
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'scale', 'city', 'contact_name', 'owner', 'created_at')
    
    # 右側篩選器
    list_filter = ('species', 'scale', 'city', 'owner')
    
    # 搜尋框
    search_fields = ('name', 'contact_name', 'phone', 'address')
    
    # 編輯時的分組顯示
    fieldsets = (
        (None, {'fields': ('name', 'owner', 'contact_name', 'phone', 'address')}),
        ('牧場分類', {'fields': ('species', 'scale', 'city')}),
    )
    
    # 確保只有 Superuser 可以新增客戶 (因為這是付費用戶功能)
    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        # 這裡未來可以改成檢查 user.is_paid_member 
        return True # 暫時開放，讓測試用戶也可以新增
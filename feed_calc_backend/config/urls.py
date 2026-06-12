# config/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView, TemplateView
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import UserPreferenceView



urlpatterns = [
    path("admin/", admin.site.urls),

    # 你的各 app
    path('api/auth/', include('accounts.urls')),
    path("api/ingredients/", include("ingredients.urls")),
    path("api/standards/", include("standards.urls")),
    path("api/formulas/", include("formulas.urls")),
    path("api/user/preferences", UserPreferenceView.as_view(), name='user-preferences'),
    #path("api/", include("analysis.urls")),
    #path("api/", include("reports.urls")),
    
    # 根路徑導向（可留可刪）
    path("", RedirectView.as_view(url="/admin/", permanent=False)),
]

    # ✨ [新增] 在開發模式下，讓 Django 負責送出靜態檔案
    # 這一行必須放在 re_path 之前！
if settings.DEBUG:
    # 1. 處理 Media 檔案 (上傳的圖片等)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # 2. 處理 Static 檔案
    #if settings.STATICFILES_DIRS:
        # 本地開發環境：從原始碼資料夾找
    #    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    #else:
        # Render 除錯模式：從收集後的 staticfiles 資料夾找
    #    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    


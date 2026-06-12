# accounts/urls.py

import sys
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from .views import RegisterView, CustomerListView

urlpatterns = []

# djoser auth endpoints are only needed for cloud deployment.
# The desktop app uses StandaloneBypassAuth (auto-login as local_admin)
# and djoser.urls cannot be bundled by PyInstaller due to AppRegistryNotReady.
if not getattr(sys, 'frozen', False):
    urlpatterns += [
        path('', include('djoser.urls')),
        path('', include('djoser.urls.authtoken')),
    ]

urlpatterns += [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='login'),
    path('customers/', CustomerListView.as_view(), name='customer-list'),
]
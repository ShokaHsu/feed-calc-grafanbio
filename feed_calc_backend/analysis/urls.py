from django.urls import path
from . import views

app_name = "analysis"

urlpatterns = [
    # /api/analysis/gap/
    path("analysis/gap/", views.gap_analysis, name="gap"),
    # /api/analysis/cost/
    path("analysis/cost/", views.cost_analysis, name="cost"),
]

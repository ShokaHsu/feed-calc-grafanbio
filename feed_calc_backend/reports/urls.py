from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    # /api/reports/formula/<pk>.pdf
    path("reports/formula/<int:pk>.pdf", views.formula_pdf, name="formula_pdf"),
]

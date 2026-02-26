from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="visualization_dashboard"),
    path("demographics/", views.demographics_view, name="visualization_demographics"),
    path("trends/", views.trends_view, name="visualization_trends"),
    path("reports/", views.reports_view, name="visualization_reports"),
    path("reports/export/pdf/", views.export_pdf, name="export_pdf"),
    path("reports/export/word/", views.export_word, name="export_word"),
    path("reports/export/excel/", views.export_excel, name="export_excel"),
]



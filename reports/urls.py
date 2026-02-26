from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="reports_dashboard"),

    # Visualization
    path("visualization/", views.visualization_reports, name="reports_visualization"),

    # Indicators
    path("indicators/", views.indicator_reports, name="reports_indicators"),

    # Analysis
    path("analysis/", views.analysis_reports, name="reports_analysis"),

    # Policy
    path("policy/", views.policy_reports, name="reports_policy"),
    path("policy/pdf/", views.policy_reports_pdf, name="reports_policy_pdf"),

    # Violence Reports
    path("violence/", views.violence_reports, name="violence_reports"),
    path("violence/pdf/", views.export_violence_pdf, name="export_violence_pdf"),
    path("violence/excel/", views.export_violence_excel, name="export_violence_excel"),

    # Data Collection Reports
    path("datacollection/", views.datacollection_reports, name="reports_datacollection"),
    path("datacollection/excel/", views.export_datacollection_excel, name="export_datacollection_excel"),
]


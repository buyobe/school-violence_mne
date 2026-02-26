from django.urls import path
from . import views

app_name = "data_collection"

urlpatterns = [
    path("", views.data_dashboard, name="data_dashboard"),
    path("dashboard/", views.data_dashboard, name="data_dashboard"),
    path("upload/", views.upload_excel, name="upload_excel"),
    path("list/", views.data_list, name="data_list"),   # <-- this is the key
    path("analysis/", views.data_analysis, name="data_analysis"),
    path("export_students/", views.export_students, name="export_students"),
    path("export_teachers/", views.export_teachers, name="export_teachers"),
    path("export_parents/", views.export_parents, name="export_parents"),
    path("ajax/get-districts/", views.get_districts, name="get_districts"),
    path("ajax/get-schools/", views.get_schools, name="get_schools"),
    path("ajax/get-teacher-levels/", views.get_teacher_levels, name="get_teacher_levels"),
    path("ajax/get-parent-jobs/", views.get_parent_employment, name="get_parent_employment"),
]

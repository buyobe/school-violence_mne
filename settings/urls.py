from django.urls import path
from . import views

app_name = "settings"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("users/", views.user_list, name="user_list"),
    path("users/add/", views.add_user, name="add_user"),
    path("users/<int:user_id>/edit/", views.edit_user, name="edit_user"),
    path("users/<int:user_id>/delete/", views.delete_user, name="delete_user"),
    path("role-redirect/", views.role_redirect_view, name="role_redirect"),
    path("backup/", views.backup_database, name="backup_database"),
    path("restore/", views.restore_database, name="restore_database"),
    path("system/", views.system_settings, name="system_settings"),

]


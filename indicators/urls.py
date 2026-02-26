from django.shortcuts import redirect
from django.urls import path
from . import views

urlpatterns = [
    path("", views.indicators_dashboard, name="indicators_dashboard"),
    path("edit/<int:pk>/", views.edit_indicator, name="edit_indicator"),
    path("delete/<int:pk>/", views.delete_indicator, name="delete_indicator"),
]

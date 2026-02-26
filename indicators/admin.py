from django.contrib import admin
from .models import Indicator

@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ("name", "indicator_type", "target_value", "actual_value")
    search_fields = ("name", "indicator_type")

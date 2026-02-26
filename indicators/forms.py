from django import forms
from .models import Indicator

class IndicatorForm(forms.ModelForm):
    class Meta:
        model = Indicator
        fields = ["name", "indicator_type", "target_value", "actual_value", "description", "proof_document"]

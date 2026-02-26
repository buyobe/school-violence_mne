
from django import forms

class UploadExcelForm(forms.Form):
    excel_file = forms.FileField(
        label="Upload Excel File",
        help_text="Upload an .xlsx file with sheets named Students, Teachers, Parents"
    )

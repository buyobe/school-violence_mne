from django.db import models

class Indicator(models.Model):
    TYPE_CHOICES = [
        ("input", "Input"),
        ("output", "Output"),
        ("outcome", "Outcome"),
        ("impact", "Impact"),
    ]

    name = models.CharField(max_length=200)
    indicator_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    target_value = models.IntegerField(default=0)
    actual_value = models.IntegerField(default=0)
    description = models.TextField(default="", blank=True)
    proof_document = models.FileField(upload_to="indicator_proofs/", blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.indicator_type})"

    @property
    def progress_percentage(self):
        if self.target_value > 0:
            return int((self.actual_value / self.target_value) * 100)
        return 0

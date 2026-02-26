from django.db import models
from django.utils import timezone


class Student(models.Model):
    id_number = models.CharField(max_length=50, unique=True, null=True, blank=True)   # custom unique ID
    region = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    school = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    age_group = models.CharField(max_length=50, blank=True)
    disability_status = models.BooleanField(default=False)
    knowledge_on_violence = models.BooleanField(default=False)
    experienced_vac = models.BooleanField(default=False)  # Experienced any VAC
    forms_of_violence = models.TextField(blank=True)
    perpetrators = models.TextField(blank=True)
    vulnerable_places = models.TextField(blank=True)
    reporting_violence = models.BooleanField(default=False)
    effectiveness_reporting_system = models.CharField(max_length=200, blank=True)  # Effectiveness of Reporting System

    

    def __str__(self):
        return f"Student {self.id_number} - {self.region}/{self.school}"


class Teacher(models.Model):
    id_number = models.CharField(max_length=50, unique=True, null=True, blank=True)  # custom unique ID
    region = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    school = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    age_group = models.CharField(max_length=50, blank=True)
    marital_status = models.CharField(max_length=50, blank=True)
    education_level = models.CharField(max_length=100, blank=True)
    forms_of_violence = models.TextField(blank=True)
    reporting_violence = models.BooleanField(default=False)
    vulnerable_places = models.TextField(blank=True)

    # Newly added fields
    right_to_discipline_child = models.BooleanField(default=False)
    effective_handling_vac = models.CharField(max_length=200, blank=True)
    training_received = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Teacher {self.id_number} - {self.region}/{self.school}"


class Parent(models.Model):
    id_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    region = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    school = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    age_group = models.CharField(max_length=50, blank=True)
    marital_status = models.CharField(max_length=50, blank=True)
    education_level = models.CharField(max_length=100, blank=True)
    forms_of_violence = models.TextField(blank=True)
    reporting_violence = models.BooleanField(default=False)
    vulnerable_places = models.TextField(blank=True)

    # Newly added fields
    employment = models.CharField(max_length=100, blank=True)
    physical_punishment = models.BooleanField(default=False)
    believe_in_child_punishment = models.BooleanField(default=False)
    effectiveness_positive_punishment = models.CharField(max_length=200, blank=True)
    child_comforting = models.BooleanField(default=False)
    impose_rules_to_child = models.BooleanField(default=False)
    set_rules_with_child = models.BooleanField(default=False)

    def __str__(self):
        return f"Parent {self.id_number} - {self.region}/{self.school}"

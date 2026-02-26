from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import Student, Teacher, Parent
from .resources import StudentResource, TeacherResource, ParentResource


@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):
    resource_class = StudentResource
    list_display = ("id_number", "region", "district", "school", "gender", "age_group", "reporting_violence", "experienced_vac")
    search_fields = ("id_number", "region", "district", "school", "gender", "age_group")

    fieldsets = (
        ("Identification", {
            "fields": ("id_number", "region", "district", "school", "gender", "age_group", "disability_status")
        }),
        ("Violence Knowledge & Experience", {
            "fields": ("knowledge_on_violence", "experienced_vac", "forms_of_violence", "perpetrators", "vulnerable_places")
        }),
        ("Reporting", {
            "fields": ("reporting_violence", "effectiveness_reporting_system")
        }),
    )


@admin.register(Teacher)
class TeacherAdmin(ImportExportModelAdmin):
    resource_class = TeacherResource
    list_display = ("id_number", "region", "district", "school", "gender", "age_group", "reporting_violence", "right_to_discipline_child")
    search_fields = ("id_number", "region", "district", "school", "gender", "age_group")

    fieldsets = (
        ("Identification", {
            "fields": ("id_number", "region", "district", "school", "gender", "age_group", "marital_status", "education_level")
        }),
        ("Violence & Reporting", {
            "fields": ("forms_of_violence", "reporting_violence", "vulnerable_places")
        }),
        ("Discipline & Training", {
            "fields": ("right_to_discipline_child", "effective_handling_vac", "training_received")
        }),
    )


@admin.register(Parent)
class ParentAdmin(ImportExportModelAdmin):
    resource_class = ParentResource
    list_display = ("id_number", "region", "district", "school", "gender", "age_group", "employment", "reporting_violence")
    search_fields = ("id_number", "region", "district", "school", "gender", "age_group")

    fieldsets = (
        ("Identification", {
            "fields": ("id_number", "region", "district", "school", "gender", "age_group", "marital_status", "education_level", "employment")
        }),
        ("Discipline Practices", {
            "fields": ("physical_punishment", "believe_in_child_punishment", "effectiveness_positive_punishment", "child_comforting", "impose_rules_to_child", "set_rules_with_child")
        }),
        ("Violence & Reporting", {
            "fields": ("forms_of_violence", "reporting_violence", "vulnerable_places")
        }),
    )

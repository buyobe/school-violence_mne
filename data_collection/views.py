from django.shortcuts import render, redirect
import pandas as pd
import csv
from django.http import HttpResponse
from django.core.paginator import Paginator
from .models import Student, Teacher, Parent
from .forms import UploadExcelForm
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required

@login_required
def data_list(request):
    student_list = Student.objects.all()
    teacher_list = Teacher.objects.all()
    parent_list = Parent.objects.all()

    student_paginator = Paginator(student_list, 10)
    teacher_paginator = Paginator(teacher_list, 10)
    parent_paginator = Paginator(parent_list, 10)

    students = student_paginator.get_page(request.GET.get("student_page"))
    teachers = teacher_paginator.get_page(request.GET.get("teacher_page"))
    parents = parent_paginator.get_page(request.GET.get("parent_page"))

    return render(request, "data_collection/data_list.html", {
        "students": students,
        "teachers": teachers,
        "parents": parents,
    })


@login_required
def data_dashboard(request):
    # --- Students ---
    total_students = Student.objects.count()
    students_by_gender = Student.objects.values("gender").annotate(count=Count("id"))
    students_by_disability = Student.objects.values("disability_status").annotate(count=Count("id"))

    # --- Teachers ---
    total_teachers = Teacher.objects.count()
    teachers_by_gender = Teacher.objects.values("gender").annotate(count=Count("id"))
    teachers_by_training = Teacher.objects.values("training_received").annotate(count=Count("id"))

    # --- Parents ---
    total_parents = Parent.objects.count()
    parents_by_gender = Parent.objects.values("gender").annotate(count=Count("id"))

    # --- Overall by Region ---
    regions = set(
        list(Student.objects.values_list("region", flat=True)) +
        list(Teacher.objects.values_list("region", flat=True)) +
        list(Parent.objects.values_list("region", flat=True))
    )
    overall_by_region = []
    for region in regions:
        overall_by_region.append({
            "region": region,
            "student_count": Student.objects.filter(region=region).count(),
            "teacher_count": Teacher.objects.filter(region=region).count(),
            "parent_count": Parent.objects.filter(region=region).count(),
        })

    # --- Overall by District ---
    districts = set(
        list(Student.objects.values_list("district", flat=True)) +
        list(Teacher.objects.values_list("district", flat=True)) +
        list(Parent.objects.values_list("district", flat=True))
    )
    overall_by_district = []
    for district in districts:
        overall_by_district.append({
            "district": district,
            "student_count": Student.objects.filter(district=district).count(),
            "teacher_count": Teacher.objects.filter(district=district).count(),
            "parent_count": Parent.objects.filter(district=district).count(),
        })

    # --- Overall by School ---
    schools = set(
        list(Student.objects.values_list("school", flat=True)) +
        list(Teacher.objects.values_list("school", flat=True)) +
        list(Parent.objects.values_list("school", flat=True))
    )
    overall_by_school = []
    for school in schools:
        overall_by_school.append({
            "school": school,
            "student_count": Student.objects.filter(school=school).count(),
            "teacher_count": Teacher.objects.filter(school=school).count(),
            "parent_count": Parent.objects.filter(school=school).count(),
        })

    context = {
        "total_students": total_students,
        "students_by_gender": students_by_gender,
        "students_by_disability": students_by_disability,
        "total_teachers": total_teachers,
        "teachers_by_gender": teachers_by_gender,
        "teachers_by_training": teachers_by_training,
        "total_parents": total_parents,
        "parents_by_gender": parents_by_gender,
        "overall_by_region": overall_by_region,
        "overall_by_district": overall_by_district,
        "overall_by_school": overall_by_school,
    }
    return render(request, "data_collection/dashboard.html", context)



# -------------------------------
# AJAX Endpoints for Dependent Dropdowns
# -------------------------------
@login_required
def get_districts(request):
    region = request.GET.get("region")
    districts = []
    if region:
        districts = Student.objects.filter(region=region).values_list("district", flat=True).distinct()
    return JsonResponse({"districts": list(districts)})
@login_required
def get_schools(request):
    district = request.GET.get("district")
    schools = []
    if district:
        schools = Student.objects.filter(district=district).values_list("school", flat=True).distinct()
    return JsonResponse({"schools": list(schools)})
@login_required
def get_teacher_levels(request):
    levels = Teacher.objects.values_list("education_level", flat=True).distinct()
    return JsonResponse({"levels": list(levels)})
@login_required
def get_parent_employment(request):
    jobs = Parent.objects.values_list("employment", flat=True).distinct()
    return JsonResponse({"jobs": list(jobs)})

# -------------------------------
# Analysis View
# -------------------------------
@login_required
def data_analysis(request):
    # Get filters
    region = request.GET.get("region") or None
    district = request.GET.get("district") or None
    school = request.GET.get("school") or None
    gender = request.GET.get("gender") or None
    age_group = request.GET.get("age_group") or None
    disability_status = request.GET.get("disability_status") or None
    teacher_level = request.GET.get("education_level") or None
    parent_job = request.GET.get("employment") or None

    students = Student.objects.all()
    teachers = Teacher.objects.all()
    parents = Parent.objects.all()

    # Apply filters
    if region:
        students = students.filter(region=region)
        teachers = teachers.filter(region=region)
        parents = parents.filter(region=region)
    if district:
        students = students.filter(district=district)
        teachers = teachers.filter(district=district)
        parents = parents.filter(district=district)
    if school:
        students = students.filter(school=school)
        teachers = teachers.filter(school=school)
        parents = parents.filter(school=school)
    if gender:
        students = students.filter(gender__iexact=gender)
        teachers = teachers.filter(gender__iexact=gender)
        parents = parents.filter(gender__iexact=gender)
    if age_group:
        students = students.filter(age_group=age_group)
        teachers = teachers.filter(age_group=age_group)
        parents = parents.filter(age_group=age_group)
    if disability_status in ["true", "false"]:
        students = students.filter(disability_status=(disability_status == "true"))
    if teacher_level:
        teachers = teachers.filter(education_level=teacher_level)
    if parent_job:
        parents = parents.filter(employment=parent_job)

    # Counts
    student_count = students.count()
    teacher_count = teachers.count()
    parent_count = parents.count()

    # Chart breakdowns
    student_gender_data = {
        "Male": students.filter(gender__iexact="Male").count(),
        "Female": students.filter(gender__iexact="Female").count(),
    }
    teacher_gender_data = {
        "Male": teachers.filter(gender__iexact="Male").count(),
        "Female": teachers.filter(gender__iexact="Female").count(),
    }
    parent_gender_data = {
        "Male": parents.filter(gender__iexact="Male").count(),
        "Female": parents.filter(gender__iexact="Female").count(),
    }

    # Distinct values for dropdowns
    regions = Student.objects.values_list("region", flat=True).distinct()
    districts = Student.objects.values_list("district", flat=True).distinct()
    schools = Student.objects.values_list("school", flat=True).distinct()
    genders = Student.objects.values_list("gender", flat=True).distinct()
    age_groups = Student.objects.values_list("age_group", flat=True).distinct()
    teacher_levels = Teacher.objects.values_list("education_level", flat=True).distinct()
    parent_jobs = Parent.objects.values_list("employment", flat=True).distinct()

    #......Added for new analysis templates
    cases_by_region = Student.objects.values("region").annotate(count=Count("id")).order_by("-count")
    cases_by_district = Student.objects.values("district").annotate(count=Count("id")).order_by("-count")
    cases_by_school = Student.objects.values("school").annotate(count=Count("id")).order_by("-count")
    violence_types_overall = Student.objects.values("forms_of_violence").annotate(count=Count("id")).order_by("-count")

    top_region = cases_by_region.first() if cases_by_region else None
    top_district = cases_by_district.first() if cases_by_district else None
    top_school = cases_by_school.first() if cases_by_school else None
    top_violence = violence_types_overall.first() if violence_types_overall else None
    # .....


    return render(request, "data_collection/analysis.html", {
        #........new analysis 
        "top_region": top_region,
        "top_district": top_district,
        "top_school": top_school,
        "top_violence": top_violence,
        "violence_types_overall": violence_types_overall,
        #......
        "students": students,
        "teachers": teachers,
        "parents": parents,
        "student_count": student_count,
        "teacher_count": teacher_count,
        "parent_count": parent_count,
        "student_gender_data": student_gender_data,
        "teacher_gender_data": teacher_gender_data,
        "parent_gender_data": parent_gender_data,
        "filters": {
            "region": region or "",
            "district": district or "",
            "school": school or "",
            "gender": gender or "",
            "age_group": age_group or "",
            "disability_status": disability_status or "",
            "education_level": teacher_level or "",
            "employment": parent_job or "",
        },
        "regions": regions,
        "districts": districts,
        "schools": schools,
        "genders": genders,
        "age_groups": age_groups,
        "teacher_levels": teacher_levels,
        "parent_jobs": parent_jobs,
    })


'''#............................
#Analysis View
#.............................
def data_analysis(request):
    # Get filters
    region = request.GET.get("region") or None
    district = request.GET.get("district") or None
    school = request.GET.get("school") or None
    gender = request.GET.get("gender") or None
    age_group = request.GET.get("age_group") or None
    disability_status = request.GET.get("disability_status") or None

    students = Student.objects.all()
    teachers = Teacher.objects.all()
    parents = Parent.objects.all()

    # Apply filters (same as before)
    if region:
        students = students.filter(region=region)
        teachers = teachers.filter(region=region)
        parents = parents.filter(region=region)
    if district:
        students = students.filter(district=district)
        teachers = teachers.filter(district=district)
        parents = parents.filter(district=district)
    if school:
        students = students.filter(school=school)
        teachers = teachers.filter(school=school)
        parents = parents.filter(school=school)
    if gender:
        students = students.filter(gender__iexact=gender)
        teachers = teachers.filter(gender__iexact=gender)
        parents = parents.filter(gender__iexact=gender)
    if age_group:
        students = students.filter(age_group=age_group)
        teachers = teachers.filter(age_group=age_group)
        parents = parents.filter(age_group=age_group)
    if disability_status in ["true", "false"]:
        students = students.filter(disability_status=(disability_status == "true"))

    # Counts
    student_count = students.count()
    teacher_count = teachers.count()
    parent_count = parents.count()

    # Chart breakdowns
    student_gender_data = {
        "Male": students.filter(gender__iexact="Male").count(),
        "Female": students.filter(gender__iexact="Female").count(),
    }
    teacher_gender_data = {
        "Male": teachers.filter(gender__iexact="Male").count(),
        "Female": teachers.filter(gender__iexact="Female").count(),
    }
    parent_gender_data = {
        "Male": parents.filter(gender__iexact="Male").count(),
        "Female": parents.filter(gender__iexact="Female").count(),
    }

    # Distinct values for dropdowns
    regions = Student.objects.values_list("region", flat=True).distinct()
    districts = Student.objects.values_list("district", flat=True).distinct()
    schools = Student.objects.values_list("school", flat=True).distinct()
    genders = Student.objects.values_list("gender", flat=True).distinct()
    age_groups = Student.objects.values_list("age_group", flat=True).distinct()

    return render(request, "data_collection/analysis.html", {
        "students": students,
        "teachers": teachers,
        "parents": parents,
        "student_count": student_count,
        "teacher_count": teacher_count,
        "parent_count": parent_count,
        "student_gender_data": student_gender_data,
        "teacher_gender_data": teacher_gender_data,
        "parent_gender_data": parent_gender_data,
        "filters": {
            "region": region or "",
            "district": district or "",
            "school": school or "",
            "gender": gender or "",
            "age_group": age_group or "",
            "disability_status": disability_status or "",
        },
        "regions": regions,
        "districts": districts,
        "schools": schools,
        "genders": genders,
        "age_groups": age_groups,
    })
#............................
#End of Analysis View
#.............................'''

# -------------------------------
# Export Functions
# -------------------------------
@login_required
def export_students(request):
    region = request.GET.get("region") or None
    district = request.GET.get("district") or None
    school = request.GET.get("school") or None
    gender = request.GET.get("gender") or None
    age_group = request.GET.get("age_group") or None
    disability_status = request.GET.get("disability_status") or None

    students = Student.objects.all()
    if region: students = students.filter(region=region)
    if district: students = students.filter(district=district)
    if school: students = students.filter(school=school)
    if gender: students = students.filter(gender__iexact=gender)
    if age_group: students = students.filter(age_group=age_group)
    if disability_status in ["true", "false"]:
        students = students.filter(disability_status=(disability_status == "true"))

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="students_filtered.csv"'
    writer = csv.writer(response)
    writer.writerow([
        "id_number","region","district","school","gender","age_group",
        "disability_status","knowledge_on_violence","experienced_vac",
        "forms_of_violence","perpetrators","vulnerable_places",
        "reporting_violence","effectiveness_reporting_system"
    ])
    for s in students:
        writer.writerow([
            s.id_number, s.region, s.district, s.school, s.gender, s.age_group,
            s.disability_status, s.knowledge_on_violence, s.experienced_vac,
            s.forms_of_violence, s.perpetrators, s.vulnerable_places,
            s.reporting_violence, s.effectiveness_reporting_system
        ])
    return response

@login_required
def export_teachers(request):
    region = request.GET.get("region") or None
    district = request.GET.get("district") or None
    school = request.GET.get("school") or None
    gender = request.GET.get("gender") or None
    age_group = request.GET.get("age_group") or None

    teachers = Teacher.objects.all()
    if region: teachers = teachers.filter(region=region)
    if district: teachers = teachers.filter(district=district)
    if school: teachers = teachers.filter(school=school)
    if gender: teachers = teachers.filter(gender__iexact=gender)
    if age_group: teachers = teachers.filter(age_group=age_group)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="teachers_filtered.csv"'
    writer = csv.writer(response)
    writer.writerow([
        "id_number","region","district","school","gender","age_group",
        "marital_status","education_level","forms_of_violence",
        "reporting_violence","vulnerable_places","right_to_discipline_child",
        "effective_handling_vac","training_received"
    ])
    for t in teachers:
        writer.writerow([
            t.id_number, t.region, t.district, t.school, t.gender, t.age_group,
            t.marital_status, t.education_level, t.forms_of_violence,
            t.reporting_violence, t.vulnerable_places, t.right_to_discipline_child,
            t.effective_handling_vac, t.training_received
        ])
    return response

@login_required
def export_parents(request):
    region = request.GET.get("region") or None
    district = request.GET.get("district") or None
    school = request.GET.get("school") or None
    gender = request.GET.get("gender") or None
    age_group = request.GET.get("age_group") or None

    parents = Parent.objects.all()
    if region: parents = parents.filter(region=region)
    if district: parents = parents.filter(district=district)
    if school: parents = parents.filter(school=school)
    if gender: parents = parents.filter(gender__iexact=gender)
    if age_group: parents = parents.filter(age_group=age_group)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="parents_filtered.csv"'
    writer = csv.writer(response)
    writer.writerow([
        "id_number","region","district","school","gender","age_group",
        "marital_status","education_level","employment","forms_of_violence",
        "reporting_violence","vulnerable_places","physical_punishment",
        "believe_in_child_punishment","effectiveness_positive_punishment",
        "child_comforting","impose_rules_to_child","set_rules_with_child","created_at"
    ])
    for p in parents:
        writer.writerow([
            p.id_number, p.region, p.district, p.school, p.gender, p.age_group,
            p.marital_status, p.education_level, p.employment, p.forms_of_violence,
            p.reporting_violence, p.vulnerable_places, p.physical_punishment,
            p.believe_in_child_punishment, p.effectiveness_positive_punishment,
            p.child_comforting, p.impose_rules_to_child, p.set_rules_with_child,
            p.created_at
        ])
    return response
# -------------------------------
# End of Export function
# -------------------------------

# -------------------------------
# Analysis View
# -------------------------------
@login_required
def data_analysis(request):
    region = request.GET.get("region") or None
    district = request.GET.get("district") or None
    school = request.GET.get("school") or None
    gender = request.GET.get("gender") or None
    age_group = request.GET.get("age_group") or None
    disability_status = request.GET.get("disability_status") or None

    students = Student.objects.all()
    teachers = Teacher.objects.all()
    parents = Parent.objects.all()

    # Apply filters
    if region:
        students = students.filter(region=region)
        teachers = teachers.filter(region=region)
        parents = parents.filter(region=region)
    if district:
        students = students.filter(district=district)
        teachers = teachers.filter(district=district)
        parents = parents.filter(district=district)
    if school:
        students = students.filter(school=school)
        teachers = teachers.filter(school=school)
        parents = parents.filter(school=school)
    if gender:
        students = students.filter(gender__iexact=gender)
        teachers = teachers.filter(gender__iexact=gender)
        parents = parents.filter(gender__iexact=gender)
    if age_group:
        students = students.filter(age_group=age_group)
        teachers = teachers.filter(age_group=age_group)
        parents = parents.filter(age_group=age_group)
    if disability_status in ["true", "false"]:
        students = students.filter(disability_status=(disability_status == "true"))

    # Counts
    # Counts
    total_students = students.count()
    total_teachers = teachers.count()
    total_parents = parents.count()

    # Reporting violence counts (adjust field name to match your models)
    reporting_students = students.filter(reporting_violence=True).count()
    reporting_teachers = teachers.filter(reporting_violence=True).count()
    reporting_parents = parents.filter(reporting_violence=True).count()


    # Chart breakdowns
    # Student charts
    student_gender_chart = {
        "labels": ["Male", "Female"],
        "values": [
            students.filter(gender__iexact="Male").count(),
            students.filter(gender__iexact="Female").count(),
        ],
    }
    student_reporting_chart = {
        "labels": ["Reporting", "Not Reporting"],
        "values": [reporting_students, total_students - reporting_students],
    }

    # Teacher charts
    teacher_gender_chart = {
        "labels": ["Male", "Female"],
        "values": [
            teachers.filter(gender__iexact="Male").count(),
            teachers.filter(gender__iexact="Female").count(),
        ],
    }
    teacher_reporting_chart = {
        "labels": ["Reporting", "Not Reporting"],
        "values": [reporting_teachers, total_teachers - reporting_teachers],
    }

    # Parent charts
    parent_gender_chart = {
        "labels": ["Male", "Female"],
        "values": [
            parents.filter(gender__iexact="Male").count(),
            parents.filter(gender__iexact="Female").count(),
        ],
    }
    parent_reporting_chart = {
        "labels": ["Reporting", "Not Reporting"],
        "values": [reporting_parents, total_parents - reporting_parents],
    }

    # Combined chart
    combined_chart = {
        "labels": ["Students", "Teachers", "Parents"],
        "values": [reporting_students, reporting_teachers, reporting_parents],
    }


    return render(request, "data_collection/analysis.html", {
    "regions": Student.objects.values_list("region", flat=True).distinct(),
    "districts": Student.objects.values_list("district", flat=True).distinct(),
    "schools": Student.objects.values_list("school", flat=True).distinct(),
    "genders": Student.objects.values_list("gender", flat=True).distinct(),
    "disability_options": ["true", "false"],

    "region": request.GET.get("region") or "",
    "district": request.GET.get("district") or "",
    "school": request.GET.get("school") or "",
    "gender": request.GET.get("gender") or "",
    "disability_status": request.GET.get("disability_status") or "",

    "total_students": total_students,
    "reporting_students": reporting_students,
    "student_gender_chart": student_gender_chart,
    "student_reporting_chart": student_reporting_chart,

    "total_teachers": total_teachers,
    "reporting_teachers": reporting_teachers,
    "teacher_gender_chart": teacher_gender_chart,
    "teacher_reporting_chart": teacher_reporting_chart,

    "total_parents": total_parents,
    "reporting_parents": reporting_parents,
    "parent_gender_chart": parent_gender_chart,
    "parent_reporting_chart": parent_reporting_chart,

    "combined_chart": combined_chart,
    })


# -------------------------------
# End of Analysis View
# -------------------------------
@login_required
def upload_excel(request):
    if request.method == "POST":
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES["excel_file"]
            xls = pd.ExcelFile(excel_file)

            # Normalize sheet names once
            sheet_names = [s.strip().lower() for s in xls.sheet_names]
            print("Detected sheets:", sheet_names)  # Debug

            def to_bool(value):
                return str(value).strip().lower() in ["yes", "true", "1", "y"]

            def normalize_columns(df):
                df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
                return df

            def normalize_value(value):
                """Trim spaces, unify capitalization, handle NaN."""
                if pd.isna(value):
                    return ""
                return str(value).strip().title()

            def normalize_multi(value):
                """Split comma-separated values into clean list."""
                if pd.isna(value):
                    return ""
                return ", ".join([v.strip().title() for v in str(value).split(",") if v.strip()])

            # Students
            if "students" in sheet_names:
                sheet_name = [s for s in xls.sheet_names if s.strip().lower() == "students"][0]
                df_students = pd.read_excel(xls, sheet_name=sheet_name)
                df_students = normalize_columns(df_students)
                for _, row in df_students.iterrows():
                    Student.objects.update_or_create(
                        id_number=str(row.get("id_number", "")).strip(),
                        defaults={
                            "region": normalize_value(row.get("region")),
                            "district": normalize_value(row.get("district")),
                            "school": normalize_value(row.get("school")),
                            "gender": normalize_value(row.get("gender")),
                            "age_group": normalize_value(row.get("age_group")),
                            "disability_status": to_bool(row.get("disability_status")),
                            "knowledge_on_violence": to_bool(row.get("knowledge_on_violence")),
                            "experienced_vac": to_bool(row.get("experienced_vac")),
                            "forms_of_violence": normalize_multi(row.get("forms_of_violence")),
                            "perpetrators": normalize_multi(row.get("perpetrators")),
                            "vulnerable_places": normalize_multi(row.get("vulnerable_places")),
                            "reporting_violence": to_bool(row.get("reporting_violence")),
                            "effectiveness_reporting_system": normalize_value(row.get("effectiveness_reporting_system")),
                        }
                    )

            # Teachers
            if "teachers" in sheet_names:
                sheet_name = [s for s in xls.sheet_names if s.strip().lower() == "teachers"][0]
                df_teachers = pd.read_excel(xls, sheet_name=sheet_name)
                df_teachers = normalize_columns(df_teachers)
                for _, row in df_teachers.iterrows():
                    Teacher.objects.update_or_create(
                        id_number=str(row.get("id_number", "")).strip(),
                        defaults={
                            "region": normalize_value(row.get("region")),
                            "district": normalize_value(row.get("district")),
                            "school": normalize_value(row.get("school")),
                            "gender": normalize_value(row.get("gender")),
                            "age_group": normalize_value(row.get("age_group")),
                            "marital_status": normalize_value(row.get("marital_status")),
                            "education_level": normalize_value(row.get("education_level")),
                            "forms_of_violence": normalize_multi(row.get("forms_of_violence")),
                            "reporting_violence": to_bool(row.get("reporting_violence")),
                            "vulnerable_places": normalize_multi(row.get("vulnerable_places")),
                            "right_to_discipline_child": to_bool(row.get("right_to_discipline_child")),
                            "effective_handling_vac": normalize_value(row.get("effective_handling_vac")),
                            "training_received": normalize_value(row.get("training_received")),
                        }
                    )

            # Parents
            if "parents" in sheet_names:
                sheet_name = [s for s in xls.sheet_names if s.strip().lower() == "parents"][0]
                df_parents = pd.read_excel(xls, sheet_name=sheet_name)
                df_parents = normalize_columns(df_parents)
                for _, row in df_parents.iterrows():
                    Parent.objects.update_or_create(
                        id_number=str(row.get("id_number", "")).strip(),
                        defaults={
                            "region": normalize_value(row.get("region")),
                            "district": normalize_value(row.get("district")),
                            "school": normalize_value(row.get("school")),
                            "gender": normalize_value(row.get("gender")),
                            "age_group": normalize_value(row.get("age_group")),
                            "marital_status": normalize_value(row.get("marital_status")),
                            "education_level": normalize_value(row.get("education_level")),
                            "employment": normalize_value(row.get("employment")),
                            "forms_of_violence": normalize_multi(row.get("forms_of_violence")),
                            "reporting_violence": to_bool(row.get("reporting_violence")),
                            "vulnerable_places": normalize_multi(row.get("vulnerable_places")),
                            "physical_punishment": to_bool(row.get("physical_punishment")),
                            "believe_in_child_punishment": to_bool(row.get("believe_in_child_punishment")),
                            "effectiveness_positive_punishment": normalize_value(row.get("effectiveness_positive_punishment")),
                            "child_comforting": to_bool(row.get("child_comforting")),
                            "impose_rules_to_child": to_bool(row.get("impose_rules_to_child")),
                            "set_rules_with_child": to_bool(row.get("set_rules_with_child")),
                        }
                    )

            return redirect("data_collection:data_list")  # no namespace in your project urls
    else:
        form = UploadExcelForm()
    return render(request, "data_collection/upload.html", {"form": form})

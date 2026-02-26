import io, xlsxwriter, json, re, os
from django.db.models import Count
from django.shortcuts import render
from data_collection.models import Student, Teacher, Parent 
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from collections import Counter
import datetime
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
)
#from data_collection.models import ViolenceReport   # adjust app/model name if different
from django.contrib.auth.decorators import login_required

@login_required
def visualization_reports(request):
    # Violence type distribution
    violence_data = (
        Student.objects.values("forms_of_violence")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    violence_labels = [d["forms_of_violence"] or "Unknown" for d in violence_data]
    violence_counts = [d["count"] for d in violence_data]

    # Perpetrator analysis
    perpetrator_data = (
        Student.objects.values("perpetrators")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    perpetrator_labels = [d["perpetrators"] or "Unknown" for d in perpetrator_data]
    perpetrator_counts = [d["count"] for d in perpetrator_data]

    # Regional hotspots
    regional_data = (
        Student.objects.values("region")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    regional_labels = [d["region"] or "Unknown" for d in regional_data]
    regional_counts = [d["count"] for d in regional_data]

    # Gender distribution
    gender_data = (
        Student.objects.values("gender")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    gender_labels = [d["gender"] or "Unknown" for d in gender_data]
    gender_counts = [d["count"] for d in gender_data]

    # Violence type by gender
    violence_gender_data = (
        Student.objects.values("forms_of_violence", "gender")
        .annotate(count=Count("id"))
        .order_by("forms_of_violence", "gender")
    )

    # Organize into structure: {violence_type: {"Male": x, "Female": y}}
    violence_gender_dict = {}
    for d in violence_gender_data:
        vtype = d["forms_of_violence"] or "Unknown"
        gender = d["gender"] or "Unknown"
        count = d["count"]
        if vtype not in violence_gender_dict:
            violence_gender_dict[vtype] = {"Male": 0, "Female": 0, "Unknown": 0}
        violence_gender_dict[vtype][gender] = count

    violence_gender_labels = list(violence_gender_dict.keys())
    male_counts = [violence_gender_dict[v]["Male"] for v in violence_gender_labels]
    female_counts = [violence_gender_dict[v]["Female"] for v in violence_gender_labels]
    unknown_counts = [violence_gender_dict[v]["Unknown"] for v in violence_gender_labels]

    return render(request, "reports/visualization.html", {
        "violence_labels": json.dumps(violence_labels),
        "violence_counts": json.dumps(violence_counts),
        "perpetrator_labels": json.dumps(perpetrator_labels),
        "perpetrator_counts": json.dumps(perpetrator_counts),
        "regional_labels": json.dumps(regional_labels),
        "regional_counts": json.dumps(regional_counts),
        "gender_labels": json.dumps(gender_labels),
        "gender_counts": json.dumps(gender_counts),
        "violence_gender_labels": json.dumps(violence_gender_labels),
        "male_counts": json.dumps(male_counts),
        "female_counts": json.dumps(female_counts),
        "unknown_counts": json.dumps(unknown_counts),
    })

## this is the view for violence report 

@login_required
def violence_reports(request):
    total_students = Student.objects.count()

    def calc_percentage(count):
        return round((count / total_students) * 100, 2) if total_students > 0 else 0

    gender_data = [(d["gender"], d["count"], calc_percentage(d["count"]))
                   for d in Student.objects.filter(experienced_vac=True).values("gender").annotate(count=Count("id"))]

    disability_data = [(d["disability_status"], d["count"], calc_percentage(d["count"]))
                       for d in Student.objects.filter(experienced_vac=True).values("disability_status").annotate(count=Count("id"))]

    age_data = [(d["age_group"], d["count"], calc_percentage(d["count"]))
                for d in Student.objects.filter(experienced_vac=True).values("age_group").annotate(count=Count("id"))]

    forms_data = [(d["forms_of_violence"], d["count"])
                  for d in Student.objects.values("forms_of_violence").annotate(count=Count("id"))]

    perpetrators_data = [(d["perpetrators"], d["count"])
                         for d in Student.objects.values("perpetrators").annotate(count=Count("id"))]

    places_data = [(d["vulnerable_places"], d["count"])
                   for d in Student.objects.values("vulnerable_places").annotate(count=Count("id"))]

    return render(request, "reports/violence_reports.html", {
        "total_students": total_students,
        "gender_data": gender_data,
        "disability_data": disability_data,
        "age_data": age_data,
        "forms_data": forms_data,
        "perpetrators_data": perpetrators_data,
        "places_data": places_data,
    })


# PDF Export (with FAWE logo centered and formatted tables)
@login_required
def export_violence_pdf(request):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # NGO Logo centered
    try:
        logo_path = "static/images/fawe_logo.png"
        logo = Image(logo_path, width=100, height=100)
        logo.hAlign = 'CENTER'
        elements.append(logo)
    except:
        pass

    elements.append(Paragraph("Violence Reports - FAWE TANZANIA", styles['Title']))
    elements.append(Spacer(1, 20))

    total_students = Student.objects.count()

    def calc_percentage(count):
        return round((count / total_students) * 100, 2) if total_students > 0 else 0

    sections = [
        ("Students Experienced Violence by Gender", [(d["gender"], d["count"], calc_percentage(d["count"])) for d in Student.objects.filter(experienced_vac=True).values("gender").annotate(count=Count("id"))], ["Gender", "Count", "Percentage"]),
        ("Students Experienced Violence by Disability", [(d["disability_status"], d["count"], calc_percentage(d["count"])) for d in Student.objects.filter(experienced_vac=True).values("disability_status").annotate(count=Count("id"))], ["Disability Status", "Count", "Percentage"]),
        ("Students Experienced Violence by Age Group", [(d["age_group"], d["count"], calc_percentage(d["count"])) for d in Student.objects.filter(experienced_vac=True).values("age_group").annotate(count=Count("id"))], ["Age Group", "Count", "Percentage"]),
        ("List of Forms of Violence", [(d["forms_of_violence"], d["count"]) for d in Student.objects.values("forms_of_violence").annotate(count=Count("id"))], ["Form of Violence", "Frequency"]),
        ("List of Perpetrators", [(d["perpetrators"], d["count"]) for d in Student.objects.values("perpetrators").annotate(count=Count("id"))], ["Perpetrator", "Frequency"]),
        ("Lost of Vulnerable Places", [(d["vulnerable_places"], d["count"]) for d in Student.objects.values("vulnerable_places").annotate(count=Count("id"))], ["Place", "Frequency"]),
    ]

    for title, data, headers in sections:
        elements.append(Paragraph(title, styles['Heading2']))
        table_data = [headers] + [list(row) for row in data]
        table = Table(table_data, hAlign='CENTER')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename="violence_reports_FAWE.pdf"'
    return response



# Excel Export (with formatted headers and borders)
@login_required
def export_violence_excel(request):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet("Violence Reports")

    # Format styles
    header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1, 'align': 'center'})
    cell_format = workbook.add_format({'border': 1, 'align': 'center'})

    headers = ["Category", "Label", "Count", "Percentage/Frequency"]
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)

    total_students = Student.objects.count()

    def calc_percentage(count):
        return round((count / total_students) * 100, 2) if total_students > 0 else 0

    row = 1

    # Gender
    for d in Student.objects.filter(experienced_vac=True).values("gender").annotate(count=Count("id")):
        worksheet.write(row, 0, "Gender", cell_format)
        worksheet.write(row, 1, d["gender"], cell_format)
        worksheet.write(row, 2, d["count"], cell_format)
        worksheet.write(row, 3, calc_percentage(d["count"]), cell_format)
        row += 1

    # Disability
    for d in Student.objects.filter(experienced_vac=True).values("disability_status").annotate(count=Count("id")):
        worksheet.write(row, 0, "Disability", cell_format)
        worksheet.write(row, 1, d["disability_status"], cell_format)
        worksheet.write(row, 2, d["count"], cell_format)
        worksheet.write(row, 3, calc_percentage(d["count"]), cell_format)
        row += 1

    # Age
    for d in Student.objects.filter(experienced_vac=True).values("age_group").annotate(count=Count("id")):
        worksheet.write(row, 0, "Age Group", cell_format)
        worksheet.write(row, 1, d["age_group"], cell_format)
        worksheet.write(row, 2, d["count"], cell_format)
        worksheet.write(row, 3, calc_percentage(d["count"]), cell_format)
        row += 1

    # Forms
    for d in Student.objects.values("forms_of_violence").annotate(count=Count("id")):
        worksheet.write(row, 0, "Forms of Violence", cell_format)
        worksheet.write(row, 1, d["forms_of_violence"], cell_format)
        worksheet.write(row, 2, d["count"], cell_format)
        worksheet.write(row, 3, "", cell_format)
        row += 1

    # Perpetrators
    for d in Student.objects.values("perpetrators").annotate(count=Count("id")):
        worksheet.write(row, 0, "Perpetrators", cell_format)
        worksheet.write(row, 1, d["perpetrators"], cell_format)
        worksheet.write(row, 2, d["count"], cell_format)
        worksheet.write(row, 3, "", cell_format)
        row += 1

    # Places
    for d in Student.objects.values("vulnerable_places").annotate(count=Count("id")):
        worksheet.write(row, 0, "Vulnerable Places", cell_format)
        worksheet.write(row, 1, d["vulnerable_places"], cell_format)
        worksheet.write(row, 2, d["count"], cell_format)
        worksheet.write(row, 3, "", cell_format)
        row += 1

    # Close workbook and return response
    workbook.close()
    output.seek(0)
    response = HttpResponse(
        output,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = 'attachment; filename="violence_reports_FAWE.xlsx"'
    return response

####... End of Violence report tab


def split_values(text):
    """Split text fields by commas, semicolons, or slashes."""
    if not text:
        return []
    return [re.sub(r"\s+", " ", val.strip().title()) for val in re.split(r"[;,/]", text) if val.strip()]

def dashboard(request):
    # --- Totals ---
    student_total = Student.objects.count()
    teacher_total = Teacher.objects.count()
    parent_total = Parent.objects.count()
    overall_total = student_total + teacher_total + parent_total

    # --- Gender breakdown ---
    student_male = Student.objects.filter(gender__iexact="Male").count()
    student_female = Student.objects.filter(gender__iexact="Female").count()
    teacher_male = Teacher.objects.filter(gender__iexact="Male").count()
    teacher_female = Teacher.objects.filter(gender__iexact="Female").count()
    parent_male = Parent.objects.filter(gender__iexact="Male").count()
    parent_female = Parent.objects.filter(gender__iexact="Female").count()

    # --- Disability breakdown (students only) ---
    student_disabled = Student.objects.filter(disability_status=True).count()
    student_abled = student_total - student_disabled

    # --- Reporting counts ---
    student_reporting = Student.objects.filter(reporting_violence=True).count()
    teacher_reporting = Teacher.objects.filter(reporting_violence=True).count()
    parent_reporting = Parent.objects.filter(reporting_violence=True).count()

    # --- Violence experience ---
    student_vac_total = Student.objects.filter(experienced_vac=True).count()
    student_vac_female = Student.objects.filter(experienced_vac=True, gender__iexact="Female").count()
    student_vac_disabled = Student.objects.filter(experienced_vac=True, disability_status=True).count()

    # --- Regions ranked ---
    regions = Counter()
    for s in Student.objects.exclude(region=""):
        regions.update([s.region.strip().title()])
    for t in Teacher.objects.exclude(region=""):
        regions.update([t.region.strip().title()])
    for p in Parent.objects.exclude(region=""):
        regions.update([p.region.strip().title()])
    ranked_regions = [(region, count, round((count / overall_total) * 100, 1)) for region, count in regions.most_common()]

    # --- Districts ranked ---
    districts = Counter()
    for s in Student.objects.exclude(district=""):
        districts.update([s.district.strip().title()])
    for t in Teacher.objects.exclude(district=""):
        districts.update([t.district.strip().title()])
    for p in Parent.objects.exclude(district=""):
        districts.update([p.district.strip().title()])
    ranked_districts = [(district, count, round((count / overall_total) * 100, 1)) for district, count in districts.most_common()]

    # --- Schools ranked ---
    schools = Counter()
    for s in Student.objects.exclude(school=""):
        schools.update([s.school.strip().title()])
    for t in Teacher.objects.exclude(school=""):
        schools.update([t.school.strip().title()])
    for p in Parent.objects.exclude(school=""):
        schools.update([p.school.strip().title()])
    ranked_schools = [(school, count, round((count / overall_total) * 100, 1)) for school, count in schools.most_common()]

    # --- Forms of violence ranked ---
    forms_of_violence = Counter()
    for s in Student.objects.exclude(forms_of_violence=""):
        forms_of_violence.update(split_values(s.forms_of_violence))
    for t in Teacher.objects.exclude(forms_of_violence=""):
        forms_of_violence.update(split_values(t.forms_of_violence))
    for p in Parent.objects.exclude(forms_of_violence=""):
        forms_of_violence.update(split_values(p.forms_of_violence))
    ranked_forms_of_violence = [(form, count, round((count / overall_total) * 100, 1)) for form, count in forms_of_violence.most_common()]

    # --- Perpetrators ranked (only Students have this field) ---
    perpetrators = Counter()
    for s in Student.objects.exclude(perpetrators=""):
        perpetrators.update(split_values(s.perpetrators))
    ranked_perpetrators = [(perp, count, round((count / overall_total) * 100, 1)) for perp, count in perpetrators.most_common()]

    # --- Vulnerable places ranked ---
    vulnerable_places = Counter()
    for s in Student.objects.exclude(vulnerable_places=""):
        vulnerable_places.update(split_values(s.vulnerable_places))
    for t in Teacher.objects.exclude(vulnerable_places=""):
        vulnerable_places.update(split_values(t.vulnerable_places))
    for p in Parent.objects.exclude(vulnerable_places=""):
        vulnerable_places.update(split_values(p.vulnerable_places))
    ranked_vulnerable_places = [(place, count, round((count / overall_total) * 100, 1)) for place, count in vulnerable_places.most_common()]

    # --- Context dictionary ---
    context = {
        "student_total": student_total,
        "teacher_total": teacher_total,
        "parent_total": parent_total,
        "student_male": student_male, "student_female": student_female,
        "teacher_male": teacher_male, "teacher_female": teacher_female,
        "parent_male": parent_male, "parent_female": parent_female,
        "student_disabled": student_disabled, "student_abled": student_abled,
        "student_reporting": student_reporting,
        "teacher_reporting": teacher_reporting,
        "parent_reporting": parent_reporting,
        "student_vac_total": student_vac_total,
        "student_vac_female": student_vac_female,
        "student_vac_disabled": student_vac_disabled,
        "ranked_regions": ranked_regions,
        "ranked_districts": ranked_districts,
        "ranked_schools": ranked_schools,
        "ranked_forms_of_violence": ranked_forms_of_violence,
        "ranked_perpetrators": ranked_perpetrators,
        "ranked_vulnerable_places": ranked_vulnerable_places,
    }

    # --- Summary Highlights ---
    summary_highlights = {
        "top_region": ranked_regions[0] if ranked_regions else None,
        "top_district": ranked_districts[0] if ranked_districts else None,
        "top_school": ranked_schools[0] if ranked_schools else None,
        "top_form_of_violence": ranked_forms_of_violence[0] if ranked_forms_of_violence else None,
        "top_perpetrator": ranked_perpetrators[0] if ranked_perpetrators else None,
        "top_vulnerable_place": ranked_vulnerable_places[0] if ranked_vulnerable_places else None,
    }

    context["summary_highlights"] = summary_highlights

    return render(request, "reports/dashboard.html", context)
###.......End of Dashboard view



###..Datacollection Views

@login_required
def datacollection_reports(request):
    # Fetch all records from your data collection app
    students = Student.objects.all()
    teachers = Teacher.objects.all()
    parents = Parent.objects.all()

    # Render into the template
    return render(request, "reports/datacollection.html", {
        "title": "Data Collection Reports",
        "students": students,
        "teachers": teachers,
        "parents": parents,
    })


def export_datacollection_excel(request):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})

    # Format styles
    header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1, 'align': 'center'})
    cell_format = workbook.add_format({'border': 1, 'align': 'center'})

    # --- Students Sheet ---
    ws_students = workbook.add_worksheet("Students")
    student_headers = [
        "ID Number", "Region", "District", "School", "Gender", "Age Group",
        "Disability", "Knowledge on Violence", "Experienced VAC",
        "Forms of Violence", "Perpetrators", "Vulnerable Places",
        "Reporting Violence", "Effectiveness Reporting System"
    ]
    for col, header in enumerate(student_headers):
        ws_students.write(0, col, header, header_format)

    row = 1
    for s in Student.objects.all():
        ws_students.write(row, 0, s.id_number, cell_format)
        ws_students.write(row, 1, s.region, cell_format)
        ws_students.write(row, 2, s.district, cell_format)
        ws_students.write(row, 3, s.school, cell_format)
        ws_students.write(row, 4, s.gender, cell_format)
        ws_students.write(row, 5, s.age_group, cell_format)
        ws_students.write(row, 6, "Yes" if s.disability_status else "No", cell_format)
        ws_students.write(row, 7, "Yes" if s.knowledge_on_violence else "No", cell_format)
        ws_students.write(row, 8, "Yes" if s.experienced_vac else "No", cell_format)
        ws_students.write(row, 9, s.forms_of_violence, cell_format)
        ws_students.write(row, 10, s.perpetrators, cell_format)
        ws_students.write(row, 11, s.vulnerable_places, cell_format)
        ws_students.write(row, 12, "Yes" if s.reporting_violence else "No", cell_format)
        ws_students.write(row, 13, s.effectiveness_reporting_system, cell_format)
        row += 1

    # --- Teachers Sheet ---
    ws_teachers = workbook.add_worksheet("Teachers")
    teacher_headers = [
        "ID Number", "Region", "District", "School", "Gender", "Age Group",
        "Marital Status", "Education Level", "Forms of Violence",
        "Reporting Violence", "Vulnerable Places", "Right to Discipline Child",
        "Effective Handling VAC", "Training Received"
    ]
    for col, header in enumerate(teacher_headers):
        ws_teachers.write(0, col, header, header_format)

    row = 1
    for t in Teacher.objects.all():
        ws_teachers.write(row, 0, t.id_number, cell_format)
        ws_teachers.write(row, 1, t.region, cell_format)
        ws_teachers.write(row, 2, t.district, cell_format)
        ws_teachers.write(row, 3, t.school, cell_format)
        ws_teachers.write(row, 4, t.gender, cell_format)
        ws_teachers.write(row, 5, t.age_group, cell_format)
        ws_teachers.write(row, 6, t.marital_status, cell_format)
        ws_teachers.write(row, 7, t.education_level, cell_format)
        ws_teachers.write(row, 8, t.forms_of_violence, cell_format)
        ws_teachers.write(row, 9, "Yes" if t.reporting_violence else "No", cell_format)
        ws_teachers.write(row, 10, t.vulnerable_places, cell_format)
        ws_teachers.write(row, 11, "Yes" if t.right_to_discipline_child else "No", cell_format)
        ws_teachers.write(row, 12, t.effective_handling_vac, cell_format)
        ws_teachers.write(row, 13, t.training_received, cell_format)
        row += 1

    # --- Parents Sheet ---
    ws_parents = workbook.add_worksheet("Parents")
    parent_headers = [
        "ID Number", "Region", "District", "School", "Gender", "Age Group",
        "Marital Status", "Education Level", "Forms of Violence",
        "Reporting Violence", "Vulnerable Places", "Employment",
        "Physical Punishment", "Believe in Child Punishment",
        "Effectiveness Positive Punishment", "Child Comforting",
        "Impose Rules to Child", "Set Rules with Child"
    ]
    for col, header in enumerate(parent_headers):
        ws_parents.write(0, col, header, header_format)

    row = 1
    for p in Parent.objects.all():
        ws_parents.write(row, 0, p.id_number, cell_format)
        ws_parents.write(row, 1, p.region, cell_format)
        ws_parents.write(row, 2, p.district, cell_format)
        ws_parents.write(row, 3, p.school, cell_format)
        ws_parents.write(row, 4, p.gender, cell_format)
        ws_parents.write(row, 5, p.age_group, cell_format)
        ws_parents.write(row, 6, p.marital_status, cell_format)
        ws_parents.write(row, 7, p.education_level, cell_format)
        ws_parents.write(row, 8, p.forms_of_violence, cell_format)
        ws_parents.write(row, 9, "Yes" if p.reporting_violence else "No", cell_format)
        ws_parents.write(row, 10, p.vulnerable_places, cell_format)
        ws_parents.write(row, 11, p.employment, cell_format)
        ws_parents.write(row, 12, "Yes" if p.physical_punishment else "No", cell_format)
        ws_parents.write(row, 13, "Yes" if p.believe_in_child_punishment else "No", cell_format)
        ws_parents.write(row, 14, p.effectiveness_positive_punishment, cell_format)
        ws_parents.write(row, 15, "Yes" if p.child_comforting else "No", cell_format)
        ws_parents.write(row, 16, "Yes" if p.impose_rules_to_child else "No", cell_format)
        ws_parents.write(row, 17, "Yes" if p.set_rules_with_child else "No", cell_format)
        row += 1

    # Close workbook and return response
    workbook.close()
    output.seek(0)
    response = HttpResponse(
        output,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = 'attachment; filename="datacollection_report.xlsx"'
    return response


### End of data Collection view

@login_required
def indicator_reports(request):
    total_students = Student.objects.count()

    # 1. Students reporting violence
    reporting_yes = Student.objects.filter(reporting_violence=True).count()
    reporting_no = Student.objects.filter(reporting_violence=False).count()
    reporting_rate = round((reporting_yes / total_students) * 100, 2) if total_students > 0 else 0

    # 2. Experienced vs Unexperienced VAC
    experienced_yes = Student.objects.filter(experienced_vac=True).count()
    experienced_no = Student.objects.filter(experienced_vac=False).count()
    experienced_rate = round((experienced_yes / total_students) * 100, 2) if total_students > 0 else 0
    unexperienced_rate = round((experienced_no / total_students) * 100, 2) if total_students > 0 else 0

    # 3. Forms of Violence Experienced (%)
    prevalence_data = (
        Student.objects.values("forms_of_violence")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    prevalence_labels = [d["forms_of_violence"] or "Unknown" for d in prevalence_data]
    prevalence_counts = [round((d["count"] / total_students) * 100, 2) for d in prevalence_data]

    # 4. Cases by Perpetrators (%)
    perpetrator_data = (
        Student.objects.values("perpetrators")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    perpetrator_labels = [d["perpetrators"] or "Unknown" for d in perpetrator_data]
    perpetrator_counts = [round((d["count"] / total_students) * 100, 2) for d in perpetrator_data]

    # 5. Reported vs Unreported Violence
    reported_cases = reporting_yes
    unreported_cases = reporting_no
    violence_cases = reported_cases + unreported_cases
    reported_rate = round((reported_cases / violence_cases) * 100, 2) if violence_cases > 0 else 0
    unreported_rate = round((unreported_cases / violence_cases) * 100, 2) if violence_cases > 0 else 0

    # 6. Effectiveness of Reporting System
    effective_cases = Student.objects.filter(effectiveness_reporting_system=True).count()
    ineffective_cases = Student.objects.filter(effectiveness_reporting_system=False).count()
    effectiveness_rate = round((effective_cases / reported_cases) * 100, 2) if reported_cases > 0 else 0
    unresolved_rate = round((ineffective_cases / reported_cases) * 100, 2) if reported_cases > 0 else 0

    # 7. Recurrence Rate
    recurrence_data = (
        Student.objects.values("id_number")
        .annotate(case_count=Count("id"))
        .filter(case_count__gt=1)
    )
    recurrent_students = recurrence_data.count()
    recurrence_rate = round((recurrent_students / total_students) * 100, 2) if total_students > 0 else 0
    non_recurrence_rate = round(100 - recurrence_rate, 2) if total_students > 0 else 0

    # Outcome Indicators (Disciplinary Actions) — optional if field exists
    disciplinary_data = (
        Student.objects.values("perpetrators")  # placeholder: replace with actual field if exists
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    disciplinary_labels = [d["perpetrators"] or "Unknown" for d in disciplinary_data]
    disciplinary_counts = [d["count"] for d in disciplinary_data]

    return render(request, "reports/indicators.html", {
        # Headline percentages
        "reporting_rate": reporting_rate,
        "experienced_rate": experienced_rate,
        "unexperienced_rate": unexperienced_rate,
        "reported_rate": reported_rate,
        "unreported_rate": unreported_rate,
        "effectiveness_rate": effectiveness_rate,
        "unresolved_rate": unresolved_rate,
        "recurrence_rate": recurrence_rate,
        "non_recurrence_rate": non_recurrence_rate,

        # Raw counts for charts
        "reporting_yes": reporting_yes,
        "reporting_no": reporting_no,
        "experienced_yes": experienced_yes,
        "experienced_no": experienced_no,
        "effective_cases": effective_cases,
        "ineffective_cases": ineffective_cases,

        # Labels + datasets
        "prevalence_labels": json.dumps(prevalence_labels),
        "prevalence_counts": json.dumps(prevalence_counts),
        "perpetrator_labels": json.dumps(perpetrator_labels),
        "perpetrator_counts": json.dumps(perpetrator_counts),
        "disciplinary_labels": json.dumps(disciplinary_labels),
        "disciplinary_counts": json.dumps(disciplinary_counts),
    })


###... Analysis views
@login_required
def analysis_reports(request):
    students = Student.objects.all()

    # Gender distribution
    effects_by_gender = dict(Counter(students.values_list("gender", flat=True)))

    # Age distribution
    effects_by_age = dict(Counter(students.values_list("age_group", flat=True)))

    # Perpetrators (stored as text, may need splitting if multiple values are saved)
    effects_by_perpetrator = dict(Counter(students.values_list("perpetrators", flat=True)))

    # Vulnerable places
    effects_by_place = dict(Counter(students.values_list("vulnerable_places", flat=True)))

    # Reporting effectiveness
    reporting_effectiveness = {
        "Reported": students.filter(reporting_violence=True).count(),
        "Not Reported": students.filter(reporting_violence=False).count(),
    }

    # Disability impacts
    disability_total = students.filter(disability_status=True).count()
    disability_breakdown = dict(Counter(students.values_list("forms_of_violence", flat=True)))

    context = {
        "effects_by_gender": effects_by_gender,
        "effects_by_age": effects_by_age,
        "effects_by_perpetrator": effects_by_perpetrator,
        "effects_by_place": effects_by_place,
        "reporting_effectiveness": reporting_effectiveness,
        "effects_by_disability": {"total": disability_total, "breakdown": disability_breakdown},
    }
    return render(request, "reports/analysis.html", context)



##...End of Analysis view



@login_required
def policy_reports(request):
    context = {
        "title": "POLICY REPORT ON ADDRESSING VIOLENCE IN SCHOOLS",
        "ngo_name": "FAWE - TANZANIA",
        "ngo_logo": "images/fawe_logo.png",  # path inside static/
        "executive_summary": (
            "School violence undermines student safety, learning outcomes, "
            "and Tanzania’s progress toward SDG 4 (Quality Education). "
            "Data collected from students reveals patterns of violence by gender, age, "
            "perpetrators, and reporting effectiveness. This report formalizes these findings "
            "into actionable policy recommendations to strengthen child protection systems in schools."
        ),
        "policy_table": [
            {
                "finding": "Boys and girls experience different forms of violence",
                "gap": "Policies don’t address gender‑specific vulnerabilities",
                "recommendation": "Develop gender‑responsive child protection policies; train teachers on gender‑sensitive approaches",
            },
            {
                "finding": "Younger students are disproportionately exposed",
                "gap": "Lack of age‑specific safeguards in school codes of conduct",
                "recommendation": "Introduce age‑appropriate protective measures; strengthen supervision for lower grades",
            },
            {
                "finding": "Teachers and parents frequently identified as perpetrators",
                "gap": "Weak accountability mechanisms for authority figures",
                "recommendation": "Enforce strict codes of conduct; establish disciplinary committees; mandatory reporting of incidents",
            },
            {
                "finding": "Certain school environments consistently reported as unsafe",
                "gap": "No systematic monitoring of vulnerable places",
                "recommendation": "Conduct regular safety audits; redesign school spaces; integrate safe‑school standards",
            },
            {
                "finding": "Students lack trust in reporting systems",
                "gap": "Reporting mechanisms are underused and lack confidentiality",
                "recommendation": "Establish anonymous reporting channels; strengthen child helplines; ensure follow‑up and feedback",
            },
            {
                "finding": "Survivors lack adequate support services",
                "gap": "Limited counseling and psychosocial support in schools",
                "recommendation": "Provide school‑based counseling; link survivors to community services; train peer support groups",
            },
        ],
    }
    return render(request, "reports/policy.html", context)

@login_required
def policy_reports_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="policy_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # --- Cover Page ---
    logo_path = os.path.join("static", "images", "fawe_logo.png")
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=120, height=120))
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("<b>FAWE - TANZANIA</b>", styles['Title']))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("POLICY REPORT ON ADDRESSING VIOLENCE IN SCHOOLS", styles['Heading1']))
    elements.append(Spacer(1, 20))
    today = datetime.date.today().strftime("%B %d, %Y")
    elements.append(Paragraph(f"Date: {today}", styles['Normal']))
    elements.append(PageBreak())

    # --- Executive Summary ---
    summary = (
        "School violence undermines student safety, learning outcomes, "
        "and Tanzania’s progress toward SDG 4 (Quality Education). "
        "This report formalizes findings into actionable policy recommendations "
        "to strengthen child protection systems in schools."
    )
    elements.append(Paragraph("<b>Executive Summary</b>", styles['Heading2']))
    elements.append(Paragraph(summary, styles['Normal']))
    elements.append(Spacer(1, 12))

    # --- Evidence–Policy–Action Table ---
    data = [
        [Paragraph("<b>Findings</b>", styles['Normal']),
         Paragraph("<b>Policy Gaps</b>", styles['Normal']),
         Paragraph("<b>Recommendations</b>", styles['Normal'])],
        [Paragraph("Boys and girls experience different forms of violence", styles['Normal']),
         Paragraph("Policies don’t address gender vulnerabilities", styles['Normal']),
         Paragraph("Develop gender-responsive child protection policies; train teachers on gender-sensitive approaches", styles['Normal'])],
        [Paragraph("Younger students disproportionately exposed", styles['Normal']),
         Paragraph("No age-specific safeguards", styles['Normal']),
         Paragraph("Introduce age-appropriate protective measures; strengthen supervision for lower grades", styles['Normal'])],
        [Paragraph("Teachers and parents frequently identified as perpetrators", styles['Normal']),
         Paragraph("Weak accountability mechanisms", styles['Normal']),
         Paragraph("Enforce strict codes of conduct; establish disciplinary committees; mandatory reporting of incidents", styles['Normal'])],
        [Paragraph("Certain school environments consistently unsafe", styles['Normal']),
         Paragraph("No systematic monitoring", styles['Normal']),
         Paragraph("Conduct regular safety audits; redesign school spaces; integrate safe-school standards", styles['Normal'])],
        [Paragraph("Students lack trust in reporting systems", styles['Normal']),
         Paragraph("Mechanisms lack confidentiality", styles['Normal']),
         Paragraph("Establish anonymous reporting channels; strengthen child helplines; ensure follow-up and feedback", styles['Normal'])],
        [Paragraph("Survivors lack adequate support services", styles['Normal']),
         Paragraph("Limited counseling and psychosocial support", styles['Normal']),
         Paragraph("Provide school-based counseling; link survivors to community services; train peer support groups", styles['Normal'])],
    ]

    table = Table(data, colWidths=[140, 140, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ]))
    elements.append(Paragraph("<b>Evidence – Policy – Action Table</b>", styles['Heading2']))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # --- Conclusion ---
    conclusion = (
        "Mitigating school violence requires urgent, coordinated action. "
        "By implementing these recommendations, FAWE Tanzania calls on government, NGOs, schools, "
        "and communities to collaborate in protecting students, upholding children’s rights, "
        "and ensuring safe learning environments for all."
    )
    elements.append(Paragraph("<b>Conclusion</b>", styles['Heading2']))
    elements.append(Paragraph(conclusion, styles['Normal']))

    doc.build(elements)
    return response





from data_collection.models import Student, Teacher, Parent

def student_awareness_rate():
    total = Student.objects.count()
    aware = Student.objects.filter(knowledge_on_violence=True).count()
    return (aware / total) * 100 if total > 0 else 0

def teacher_reporting_rate():
    total = Teacher.objects.count()
    reporting = Teacher.objects.filter(reporting_violence=True).count()
    return (reporting / total) * 100 if total > 0 else 0

def parent_reporting_rate():
    total = Parent.objects.count()
    reporting = Parent.objects.filter(reporting_violence=True).count()
    return (reporting / total) * 100 if total > 0 else 0

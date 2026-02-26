from import_export import resources
from .models import Student, Teacher, Parent

class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        fields = ('region', 'district', 'school', 'gender', 'age_group',
                  'disability_status', 'knowledge_on_violence',
                  'forms_of_violence', 'perpetrators',
                  'vulnerable_places', 'reporting_violence')
        import_id_fields = ('region', 'district', 'school')

class TeacherResource(resources.ModelResource):
    class Meta:
        model = Teacher
        fields = ('region', 'district', 'school', 'gender', 'age_group',
                  'marital_status', 'education_level',
                  'forms_of_violence', 'reporting_violence', 'vulnerable_places')
        import_id_fields = ('region', 'district', 'school')

class ParentResource(resources.ModelResource):
    class Meta:
        model = Parent
        fields = ('region', 'district', 'school', 'gender', 'age_group',
                  'marital_status', 'education_level',
                  'forms_of_violence', 'reporting_violence', 'vulnerable_places')
        import_id_fields = ('region', 'district', 'school')

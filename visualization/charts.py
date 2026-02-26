import plotly.express as px
from django.db.models import Count
from data_collection.models import Student

def violence_by_region():
    data = Student.objects.values('region').annotate(count=Count('id'))
    fig = px.bar(data, x='region', y='count', title="Violence Cases by Region")
    return fig.to_html()

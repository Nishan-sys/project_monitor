from django import forms
from .models import Projects

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Projects
        fields = ['name', 'description', 'contractor', 'start_date', 'end_date', 'estimated_cost', 'project_type']

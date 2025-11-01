from django.db import models
from user_app.models import School
from django.contrib.auth.models import User
class Projects(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('new_construction', 'New Construction'),
        ('repair', 'Repair'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    description = models.TextField()
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, help_text="Estimated project cost")
    project_type = models.CharField(max_length=30, choices=PROJECT_TYPE_CHOICES)
    sponsor = models.CharField(max_length=200, blank=True, help_text="Funding source or sponsor name")
    contractor = models.CharField(max_length=200, blank=True, help_text="Main contractor name")
    start_date = models.DateField()
    end_date = models.DateField()
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_projects')
    # Tracking fields (recommended)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class ProjectProgress(models.Model):
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name='updates')
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    progress = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    report_file = models.FileField(upload_to='project_reports/', blank=True, null=True)
    

    def __str__(self):
        return f"{self.project.name} - {self.progress}%"
    

class ProgressPhoto(models.Model):
    progress = models.ForeignKey(ProjectProgress, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='project_photos/')

    def __str__(self):
        return f"Photo for {self.progress.project.name}"
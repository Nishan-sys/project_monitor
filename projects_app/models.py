from django.db import models
from user_app.models import School

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
    
    # Tracking fields (recommended)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
# Create your models here.

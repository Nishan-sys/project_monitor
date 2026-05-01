from django.db import models
from user_app.models import School
from django.contrib.auth.models import User
from cloudinary_storage.storage import MediaCloudinaryStorage
from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError
from cloudinary.models import CloudinaryField
from django.core.validators import MinValueValidator, MaxValueValidator

def validate_pdf(file):
    if not file.name.lower().endswith('.pdf'):
        raise ValidationError("Only PDF files are allowed.")

    if file.content_type != 'application/pdf':
        raise ValidationError("Invalid file type. Only PDF allowed.")

class Projects(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('new_construction', 'New Construction'),
        ('repair', 'Repair'),
    ]

    STATUS_CHOICES = [                   
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    description = models.TextField()
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, help_text="Estimated project cost")
    project_type = models.CharField(max_length=30, choices=PROJECT_TYPE_CHOICES)
    status = models.CharField(               
        max_length=20,
        choices=STATUS_CHOICES,
        default='ongoing'
    )
    sponsor = models.CharField(max_length=200, blank=True, help_text="Funding source or sponsor name")
    contractor = models.CharField(max_length=200, blank=True, help_text="Main contractor name")
    start_date = models.DateField()
    end_date = models.DateField()
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_projects')
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
    progress = models.IntegerField(
    validators=[MinValueValidator(0), MaxValueValidator(100)]
)
    description = models.TextField(blank=True, null=True)
    report_file = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.project.name} - {self.progress}%"
    

class ProgressPhoto(models.Model):
    progress = models.ForeignKey(ProjectProgress, on_delete=models.CASCADE, related_name='photos')
    image = CloudinaryField('image', folder='project_photos')
   
    def __str__(self):
        return f"Photo for {self.progress.project.name}"







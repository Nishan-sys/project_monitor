from django.db import models
from django.contrib.auth.models import User

class Zone(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"
    

class Division(models.Model):
    name = models.CharField(max_length=100)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='divisions')

    def __str__(self):
        return f"{self.name} ({self.zone.name})"

class School(models.Model):
    name = models.CharField(max_length=200)
    census_number = models.CharField(max_length=50, unique=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='schools')

    def __str__(self):
        return f"{self.name} ({self.census_number})"


class Profile(models.Model):
    ROLE_CHOICES = [
        ('provincial', 'Provincial Director'),
        ('zonal', 'Zonal Director'),
        ('divisional', 'Divisional Director'),
        ('principal', 'Principal'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, blank=True)
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"



class SchoolUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.OneToOneField(School, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.school.name

# Create your models here.

from django.contrib import admin
from .models import Projects

@admin.register(Projects)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'start_date', 'end_date')
    search_fields = ('name',)
    list_filter = ('school',)
# Register your models here.

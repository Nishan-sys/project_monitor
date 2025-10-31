from django.contrib import admin
from .models import Projects, ProjectProgress

@admin.register(Projects)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'start_date', 'end_date')
    search_fields = ('name',)
    list_filter = ('school',)



from django.contrib import admin
from .models import ProjectProgress, ProgressPhoto


class ProgressPhotoInline(admin.TabularInline):
    model = ProgressPhoto
    extra = 0
    readonly_fields = ('image_tag',)
    fields = ('image', 'image_tag')


@admin.register(ProjectProgress)
class ProjectProgressAdmin(admin.ModelAdmin):
    list_display = ('project', 'school', 'progress', 'date')
    inlines = [ProgressPhotoInline]


@admin.register(ProgressPhoto)
class ProgressPhotoAdmin(admin.ModelAdmin):
    list_display = ('progress', 'image_tag')


# helper method to show image preview in admin
from django.utils.html import format_html

def image_tag(obj):
    if obj.image:
        return format_html('<img src="{}" width="120" style="border-radius:8px;" />', obj.image.url)
    return "-"
image_tag.short_description = 'Preview'

ProgressPhoto.image_tag = image_tag

# Register your models here.

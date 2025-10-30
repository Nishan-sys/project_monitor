from django.urls import path
from . import views

urlpatterns = [
    path('assign/<int:school_id>/', views.assign_project, name='assign_project'),
    path('list/', views.projects_list, name='projects_list'),
    path('my-projects/', views.school_projects, name='school_projects'),
]

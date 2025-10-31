from django.urls import path
from . import views

urlpatterns = [
    path('assign/<int:school_id>/', views.assign_project, name='assign_project'),
    path('list/', views.projects_list, name='projects_list'),
    path('my-projects/', views.school_projects, name='school_projects'),
    path('add-progress/<int:project_id>', views.add_project_progress, name='project_progress'),
    path('all-progress/', views.view_all_progress, name='view_all_progress'),

]

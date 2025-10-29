from django.urls import path
from . import views

urlpatterns = [
    path('assign/<int:school_id>/', views.assign_project, name='assign_project'),
]

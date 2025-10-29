from django.shortcuts import render, get_object_or_404, redirect
from user_app.models import School
from .models import Project

def assign_project(request, school_id):
    school = get_object_or_404(School, id=school_id)

    if request.method == "POST":
        Project.objects.create(
            school=school,
            name=request.POST['name'],
            description=request.POST.get('description', ''),
            estimated_cost=request.POST['estimated_cost'],
            project_type=request.POST['project_type'],
            sponsor=request.POST.get('sponsor', ''),
            contractor=request.POST.get('contractor', ''),
            start_date=request.POST['start_date'],
            end_date=request.POST['end_date'],
        )
        return redirect('schools_list')  # adjust to your route

    return render(request, 'assign_project.html', {'school': school})

# Create your views here.

from django.shortcuts import render, get_object_or_404, redirect
from user_app.models import School, SchoolUser
from .models import Projects

def assign_project(request, school_id):
    school = get_object_or_404(School, id=school_id)

    if request.method == "POST":
        Projects.objects.create(
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
        return redirect('projects_list')  # adjust to your route

    return render(request, 'assign_project.html', {'school': school})

def projects_list(request):
    projects = Projects.objects.all().select_related('school')  # efficient query with school
    return render(request, 'projects_list.html', {'projects': projects})


def school_projects(request):
    if request.user.is_authenticated:
        school_user = SchoolUser.objects.get(user=request.user)
        projects = Projects.objects.filter(school=school_user.school)
        return render(request, 'school_projects.html', {'projects': projects})


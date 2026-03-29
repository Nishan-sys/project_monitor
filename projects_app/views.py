from django.shortcuts import render, get_object_or_404, redirect
from user_app.models import School, SchoolUser
from .models import Projects, ProjectProgress, ProgressPhoto
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProjectForm  # we’ll define this below
from django.http import HttpResponseRedirect
from django.http import StreamingHttpResponse

import requests
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import ProjectProgress



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
            assigned_by=request.user, 
        )
        return redirect('projects_list')  # adjust to your route

    return render(request, 'assign_project.html', {'school': school})

def projects_list(request):
    projects = Projects.objects.all().select_related('school')  # efficient query with school
    return render(request, 'projects_list.html', {'projects': projects})


def school_projects(request):
    if request.user.is_authenticated:
        school_user = SchoolUser.objects.get(user=request.user)
        school = school_user.school
        projects = Projects.objects.filter(school=school_user.school)
        return render(request, 'school_projects.html', {'projects': projects, 'school': school,})



@login_required
def add_project_progress(request, project_id):
    project = get_object_or_404(Projects, id=project_id)
    school_user = request.user.schooluser

    if project.school != school_user.school:
        return redirect('school_projects')

    if request.method == 'POST':
        print("FILES:", request.FILES)
        print("POST:", request.POST)
        progress = request.POST.get('progress')
        description = request.POST.get('description')
        report_file = request.FILES.get('report_file')
        photos = request.FILES.getlist('photos')  

        progress_entry = ProjectProgress.objects.create(
            project=project,
            school=school_user.school,
            progress=progress,
            description=description,
            report_file=report_file
        )

        # Save up to 4 photos
        for photo in photos[:4]:
            print("Saving photo:", photo.name)
            ProgressPhoto.objects.create(progress=progress_entry, image=photo)

        # Update project's latest progress
        project.progress = progress
        project.save()

        return redirect('school_projects')

    return render(request, 'add_project_progress.html', {'project': project})


@login_required
def view_all_progress(request):
    # Only top-level users should access this
    user = request.user

    if hasattr(user, 'schooluser'):
        # block school users
        return redirect('school_projects')

    # Provincial Director: can view all projects
    progresses = ProjectProgress.objects.all().select_related('project', 'school')

    # Zonal or Divisional Directors: filter by their area if needed
    # Example (adjust depending on your user model fields):
    # progresses = progresses.filter(school__division=user.division)

    return render(request, 'view_all_progress.html', {
        'progresses': progresses
    }) 

@login_required

def edit_project(request, project_id):
    project = get_object_or_404(Projects, id=project_id)

    # Optional: check permissions (only provincial or zonal directors)
    if project.assigned_by != request.user:
        messages.error(request, "You are not authorized to edit this project.")
        return redirect('projects_list')

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully.")
            return redirect('projects_list')
    else:
        form = ProjectForm(instance=project)

    return render(request, 'edit_project.html', {'form': form, 'project': project})


def delete_project(request, project_id):
    project = get_object_or_404(Projects, id=project_id)

    if project.assigned_by != request.user:
        messages.error(request, "You are not authorized to delete this project.")
        return redirect('projects_list')

    if request.method == 'POST':
        project.delete()
        messages.success(request, "Project deleted successfully.")
        return redirect('projects_list')

    return render(request, 'delete_confirm.html', {'project': project})

# views.py





#def download_report(request, pk):
    # progress = get_object_or_404(ProjectProgress, pk=pk)
    # if not progress.report_file:
    #     return HttpResponse("No report available.", status=404)

    # file_url = progress.report_file.url
    # response = requests.get(file_url)
    # filename = file_url.split("/")[-1]

    # return HttpResponse(
    #     response.content,
    #     content_type='application/pdf',
    #     headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    # )
    # progress = get_object_or_404(ProjectProgress, pk=pk)
    # if not progress.report_file:
    #     return HttpResponse("No report available.", status=404)

    # # Cloudinary PDF URL (raw file)
    # file_url = progress.report_file.url

    # # Simply redirect user to the Cloudinary URL
    # return HttpResponseRedirect(file_url)



# def download_report(request, pk):
#     progress = get_object_or_404(ProjectProgress, pk=pk)
#     if not progress.report_file:
#         return HttpResponse("No report available.", status=404)

#     file_url = progress.report_file.url
#     r = requests.get(file_url, stream=True)

#     filename = file_url.split("/")[-1]
#     response = StreamingHttpResponse(r.iter_content(chunk_size=8192), content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'
#     return response


def download_report(request, pk):
    progress = get_object_or_404(ProjectProgress, pk=pk)

    if not progress.report_file:
        return HttpResponse("No report available.", status=404)

    file_url = progress.report_file.url

    try:
        r = requests.get(file_url, stream=True)

        # 🔥 CRITICAL CHECK
        if r.status_code != 200:
            return HttpResponse("Failed to fetch file from Cloudinary", status=500)

        filename = file_url.split("/")[-1]

        response = StreamingHttpResponse(
            r.iter_content(chunk_size=8192),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)


   

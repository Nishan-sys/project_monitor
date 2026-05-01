from django.shortcuts import render, get_object_or_404, redirect
from user_app.models import School, SchoolUser
from .models import Projects, ProjectProgress, ProgressPhoto
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProjectForm 
from django.http import StreamingHttpResponse
import requests
from django.http import HttpResponse
from .utils.supabase_storage import upload_pdf_to_supabase
from user_app.utils import can_assign_projects, is_provincial, get_user_zone
from user_app.utils import can_assign_projects, is_provincial, is_zonal, get_user_zone


@login_required
def assign_project(request, school_id):
    # Step 1 — role check: only provincial and zonal directors allowed
    if not can_assign_projects(request.user):
        messages.error(request, "You are not authorized to assign projects.")
        return redirect('dashboard_redirect')

    school = get_object_or_404(School, id=school_id)

    # Step 2 — zone scope check: zonal directors can only assign within their zone
    if is_zonal(request.user):
        user_zone = get_user_zone(request.user)
        if school.division.zone != user_zone:
            messages.error(request, "You can only assign projects to schools in your zone.")
            return redirect('dashboard_redirect')

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
        messages.success(request, f"Project successfully assigned to {school.name}.")
        return redirect('projects_list')

    return render(request, 'assign_project.html', {'school': school})

@login_required
def projects_list(request):
    user = request.user

    if is_provincial(user):
        projects = Projects.objects.all().select_related('school', 'school__division__zone')
    elif is_zonal(user):
        user_zone = get_user_zone(user)
        projects = Projects.objects.filter(
            school__division__zone=user_zone
        ).select_related('school')
    else:
        # divisional directors, school users, others — redirect to their dashboard
        return redirect('dashboard_redirect')

    return render(request, 'projects_list.html', {'projects': projects})


@login_required
def school_projects(request):
    try:
        school_user = SchoolUser.objects.get(user=request.user)
    except SchoolUser.DoesNotExist:
        messages.error(request, "No school assigned to your account.")
        return redirect('dashboard_redirect')

    school = school_user.school
    projects = Projects.objects.filter(school=school).select_related('school')
    return render(request, 'school_projects.html', {'projects': projects, 'school': school})


@login_required
def view_all_progress(request):
    user = request.user
    if hasattr(user, 'schooluser'):
        return redirect('school_projects')
    progresses = ProjectProgress.objects.all().select_related('project', 'school')
    return render(request, 'view_all_progress.html', {
        'progresses': progresses
    }) 

@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Projects, id=project_id)
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

@login_required
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


@login_required
def add_project_progress(request, project_id):
    project = get_object_or_404(Projects, id=project_id)

    if not hasattr(request.user, 'schooluser'):
        return redirect('login')

    school_user = request.user.schooluser

    if project.school != school_user.school:
        return redirect('school_projects')

    if request.method == 'POST':
        progress = request.POST.get('progress')
        description = request.POST.get('description')
        pdf_file = request.FILES.get('report_file')
        photos = request.FILES.getlist('photos')

        if not progress:
            messages.error(request, "Progress is required.")
            return render(request, 'add_project_progress.html', {'project': project})

        try:
            progress = int(progress)
        except ValueError:
            messages.error(request, "Progress must be a number.")
            return render(request, 'add_project_progress.html', {'project': project})

        if not (0 <= progress <= 100):
            messages.error(request, "Progress must be between 0 and 100.")
            return render(request, 'add_project_progress.html', {'project': project})

        pdf_url = None

        if pdf_file:
            if not pdf_file.name.endswith('.pdf'):
                return HttpResponse("Only PDF allowed")

            try:
                import uuid
                #file_name = f"{uuid.uuid4()}_{pdf_file.name}"
                pdf_url = upload_pdf_to_supabase(pdf_file)
            except Exception as e:
                return HttpResponse(f"Error: {str(e)}")

        from django.db import transaction

        with transaction.atomic():
            progress_entry = ProjectProgress.objects.create(
                project=project,
                school=school_user.school,
                progress=progress,
                description=description,
                report_file=pdf_url
            )

            for photo in photos[:4]:
                ProgressPhoto.objects.create(
                    progress=progress_entry,
                    image=photo
                )

            
        return redirect('school_projects')

    return render(request, 'add_project_progress.html', {'project': project})


@login_required
def download_report(request, pk):
    progress = get_object_or_404(ProjectProgress, pk=pk)

    # School users can only download reports for their own school
    if hasattr(request.user, 'schooluser'):
        if progress.school != request.user.schooluser.school:
            messages.error(request, "You are not authorized to access this report.")
            return redirect('school_projects')

    if not progress.report_file:
        return HttpResponse("No report available.", status=404)

    base_url = progress.report_file.split("?")[0]

    try:
        response = requests.get(base_url, stream=True, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return HttpResponse(f"Failed to fetch report: {str(e)}", status=502)

    filename = f"report_{pk}.pdf"

    django_response = StreamingHttpResponse(
        response.iter_content(chunk_size=8192),
        content_type="application/pdf"
    )
    django_response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return django_response


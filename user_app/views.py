from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Division, School, Profile
from .utils import is_provincial, is_zonal, is_divisional,get_user_zone
from projects_app.models import ProjectProgress
from projects_app.models import Projects

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard_redirect')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard_redirect(request):
    user = request.user      
    if hasattr(user, 'profile'):
        
        role = user.profile.role
        if role == 'provincial':
            return redirect('provincial_dashboard')
        elif role == 'zonal':
            return redirect('zonal_dashboard')
        elif role == 'divisional':
            return redirect('divisional_dashboard')
        elif role == 'principal':
            return redirect('principal_dashboard')
        else:
            return redirect('school_projects')  # fallback for unknown roles

    return redirect('login')  # fallback

@login_required
def provincial_dashboard(request):
    projects = Projects.objects.all().select_related('school', 'assigned_by')
    total_projects = projects.count()
    total_schools = School.objects.filter(projects__isnull=False).distinct().count()

    # Example logic — you can adjust this based on actual progress tracking
    completed_projects = projects.filter(end_date__lte='2025-10-31').count()
    ongoing_projects = total_projects - completed_projects

    context = {
        'projects': projects,
        'total_projects': total_projects,
        'total_schools': total_schools,
        'completed_projects': completed_projects,
        'ongoing_projects': ongoing_projects,
    }
    return render(request, 'provincial_dashboard.html', context)

@login_required
def zonal_dashboard(request):
    # Ensure only zonal directors can access this
    if not is_zonal(request.user):
        messages.error(request, "You are not authorized to view this page.")
        return redirect('dashboard_redirect')

    # Get this director's zone from their profile
    profile = request.user.profile
    if not profile.zone:
        return render(request, 'error.html', {'message': 'No zone assigned to your profile.'})

    zone = profile.zone

    # All projects in this zone, regardless of who assigned them
    projects = Projects.objects.filter(
        school__division__zone=zone
    ).select_related('school', 'school__division', 'assigned_by')

    total_projects = projects.count()
    total_schools = School.objects.filter(
        division__zone=zone,
        projects__isnull=False
    ).distinct().count()
    completed_projects = projects.filter(status='completed').count()
    ongoing_projects = projects.filter(status='ongoing').count()
    on_hold_projects = projects.filter(status='on_hold').count()

    context = {
        'zone': zone,
        'projects': projects,
        'total_projects': total_projects,
        'total_schools': total_schools,
        'completed_projects': completed_projects,
        'ongoing_projects': ongoing_projects,
        'on_hold_projects': on_hold_projects,
    }
    return render(request, 'zonal_dashboard.html', context)

@login_required
def divisional_dashboard(request):
    # Role check — only divisional directors allowed
    if not is_divisional(request.user):
        messages.error(request, "You are not authorized to view this page.")
        return redirect('dashboard_redirect')

    profile = Profile.objects.filter(user=request.user).select_related('division').first()

    if not profile or not profile.division:
        return render(request, 'error.html', {'message': 'No division assigned to your profile.'})

    division = profile.division

    # All projects in this division
    projects = Projects.objects.filter(
        school__division=division
    ).select_related('school', 'school__division', 'assigned_by')

    # All progress updates for projects in this division
    progresses = ProjectProgress.objects.filter(
        project__school__division=division
    ).select_related('project', 'project__school').order_by('-date')

    # Stats
    total_projects = projects.count()
    total_schools = projects.values('school').distinct().count()
    completed_projects = projects.filter(status='completed').count()
    ongoing_projects = projects.filter(status='ongoing').count()
    on_hold_projects = projects.filter(status='on_hold').count()

    context = {
        'division': division,
        'projects': projects,
        'progresses': progresses,
        'total_projects': total_projects,
        'total_schools': total_schools,
        'completed_projects': completed_projects,
        'ongoing_projects': ongoing_projects,
        'on_hold_projects': on_hold_projects,
    }
    return render(request, 'divisional_dashboard.html', context)

@login_required
def principal_dashboard(request):
    return render(request, 'principal_dashboard.html')

'''
def index_redirect(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('login')
'''
@login_required
def division_schools(request, division_id=None):
    # Scope divisions based on role
    if is_provincial(request.user):
        divisions = Division.objects.all().select_related('zone')
    elif is_zonal(request.user):
        user_zone = get_user_zone(request.user)
        if not user_zone:
            messages.error(request, "No zone assigned to your profile.")
            return redirect('dashboard_redirect')
        divisions = Division.objects.filter(zone=user_zone).select_related('zone')
    else:
        messages.error(request, "You are not authorized to assign projects.")
        return redirect('dashboard_redirect')

    if division_id:
        selected_division = get_object_or_404(Division, id=division_id)
    else:
        selected_division = divisions.first()

    return render(request, 'division_schools.html', {
        'divisions': divisions,
        'selected_division': selected_division,
        'division_id': selected_division.id if selected_division else None,
    })

def get_schools_by_division(request, division_id):
    schools = School.objects.filter(division_id=division_id).values('id', 'name', 'census_number')
    return JsonResponse(list(schools), safe=False)
# Create your views here.

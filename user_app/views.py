from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Division, School, Profile
from projects_app.models import ProjectProgress
from projects_app.models import Projects

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            print(f"Attempting login forrrrr user: {username}")
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
    print(f"User {user.username} with ID {user.id} is accessing dashboard_redirect")        
    if hasattr(user, 'profile'):
        
        role = user.profile.role
        print(role)
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
    projects = Projects.objects.filter(assigned_by=request.user)
    total_projects = projects.count()
    total_schools = School.objects.filter(projects__assigned_by=request.user).distinct().count()
    completed_projects = projects.filter(end_date__lte='2025-10-31').count()  # adjust logic later
    pending_progress = total_projects - completed_projects

    context = {
        'projects': projects,
        'total_projects': total_projects,
        'total_schools': total_schools,
        'completed_projects': completed_projects,
        'pending_progress': pending_progress,
    }
    return render(request, 'zonal_dashboard.html', context)

@login_required
def divisional_dashboard(request):
    # Get logged-in user's profile and division
    profile = Profile.objects.filter(user=request.user).select_related('division').first()

    if not profile or not profile.division:
        return render(request, 'error.html', {'message': 'No division assigned to your profile.'})

    division = profile.division

    # ✅ Get all projects in this division
    projects = Projects.objects.filter(
        school__division=division
    ).select_related('school')

    # ✅ Get all progress updates for projects in this division
    progresses = ProjectProgress.objects.filter(
        project__school__division=division
    ).select_related('project', 'project__school')

    # ✅ Handle comment submission
    '''
    if request.method == 'POST':
        progress_id = request.POST.get('progress_id')
        comment_text = request.POST.get('comment', '').strip()
        progress = get_object_or_404(ProjectProgress, id=progress_id)

        if comment_text:
            ProgressComment.objects.create(
                progress=progress,
                director=request.user,
                comment=comment_text
            )

        return redirect('divisional_dashboard')
    '''
    return render(request, 'divisional_dashboard.html', {
        'projects': projects,
        'progresses': progresses,
        'division': division
    })

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
def division_schools(request, division_id=None):
    divisions = Division.objects.all()
    if division_id:
        selected_division = Division.objects.get(id=division_id)
    else:
        selected_division = divisions.first()
    schools = School.objects.filter(division=selected_division)
    
    return render(request, 'division_schools.html', {
        'divisions': divisions,
        'schools': schools,
        'selected_division': selected_division,
    })

def get_schools_by_division(request, division_id):
    schools = School.objects.filter(division_id=division_id).values('id', 'name', 'census_number')
    return JsonResponse(list(schools), safe=False)
# Create your views here.

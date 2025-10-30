from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Division, School

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
    return render(request, 'provincial_dashboard.html')

@login_required
def zonal_dashboard(request):
    return render(request, 'zonal_dashboard.html')

@login_required
def divisional_dashboard(request):
    return render(request, 'divisional_dashboard.html')

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

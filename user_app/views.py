from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
    print("Home View Accessed")
    return render(request, 'login.html')

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

# Create your views here.

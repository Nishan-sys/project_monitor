# users/urls.py
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    #path('', views.index_redirect, name='index'), 
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'), 
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard-redirect/', views.dashboard_redirect, name='dashboard_redirect'),
    path('provincial-dashboard/', views.provincial_dashboard, name='provincial_dashboard'),
    path('zonal-dashboard/', views.zonal_dashboard, name='zonal_dashboard'),
    path('divisional-dashboard/', views.divisional_dashboard, name='divisional_dashboard'),
    path('principal-dashboard/', views.principal_dashboard, name='principal_dashboard'),
    path('division-schools/', views.division_schools, name='division_schools'),
    path('division-schools/<int:division_id>/', views.division_schools, name='division_schools_by_id'),
    path('get-schools/<int:division_id>/', views.get_schools_by_division, name='get_schools_by_division'),
]

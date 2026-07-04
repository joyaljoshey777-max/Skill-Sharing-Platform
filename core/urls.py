from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Authentication
    path('register/customer/', views.register_customer, name='register_customer'),
    path('register/provider/', views.register_provider, name='register_provider'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    # Core App
    path('skills/', views.browse_skills, name='browse_skills'),
    path('provider/<int:provider_id>/', views.provider_profile, name='provider_profile'),
    path('provider/<int:provider_id>/book/', views.book_provider, name='book_provider'),
    
    # Dashboards
    path('dashboard/user/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/provider/', views.provider_dashboard, name='provider_dashboard'),
    path('booking/<int:booking_id>/review/', views.submit_review, name='submit_review'),
    path('booking/<int:booking_id>/<str:action>/', views.manage_booking, name='manage_booking'),
]

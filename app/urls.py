from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('student/signup/', views.StudentSignUpView.as_view(), name='student_signup'),
    path('student/login/', views.StudentLoginView.as_view(), name='student_login'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('instructor/signup/', views.InstructorSignUpView.as_view(), name='instructor_signup'),
    path('instructor/login/', views.InstructorLoginView.as_view(), name='instructor_login'),
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('support/', views.support, name='support'),
    
    # Generic auth views
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Other paths
    path('signup/', views.signup, name='signup'),  # This will redirect to landing
    path('dashboard/', views.dashboard, name='dashboard'),
    path('send-timetable/', views.send_timetable_email, name='send_timetable'),
]

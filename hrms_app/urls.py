"""
URL configuration for hrms_app.
"""
from django.urls import path
from . import views

app_name = 'hrms_app'

urlpatterns = [
    # Template-based views
    path('', views.home, name='home'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.add_employee, name='add_employee'),
    path('employees/<str:employee_id>/', views.employee_detail, name='employee_detail'),
    path('attendance/add/', views.add_attendance, name='add_attendance'),
    path('reports/', views.reports, name='reports'),
    
    # API endpoints
    path('api/employees/', views.api_employees, name='api_employees'),
    path('api/employees/<str:employee_id>/', views.api_employee_detail, name='api_employee_detail'),
    path('api/attendance/', views.api_attendance, name='api_attendance'),
]


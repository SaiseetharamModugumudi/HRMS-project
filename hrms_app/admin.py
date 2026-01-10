"""
Admin configuration for HRMS app models.
"""
from django.contrib import admin
from .models import Employee, Attendance


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    Admin interface for Employee model.
    """
    list_display = ('id', 'name', 'email', 'designation', 'department', 'date_of_joining')
    list_filter = ('department', 'designation', 'date_of_joining')
    search_fields = ('name', 'email', 'employee_id')
    ordering = ('name',)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """
    Admin interface for Attendance model.
    """
    list_display = ('employee', 'date', 'in_time', 'out_time', 'status')
    list_filter = ('date', 'status')
    search_fields = ('employee__name', 'employee__employee_id')
    date_hierarchy = 'date'
    ordering = ('-date', '-in_time')


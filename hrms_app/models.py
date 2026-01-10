"""
Database models for HRMS application.
"""
from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone


class Employee(models.Model):
    """
    Model representing an employee in the HRMS system.
    
    Attributes:
        employee_id: Unique identifier for the employee (auto-generated)
        name: Full name of the employee
        email: Email address of the employee
        phone: Contact phone number
        address: Residential address
        designation: Job title/position
        department: Department the employee belongs to
        date_of_joining: Date when employee joined the organization
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """
    
    DESIGNATION_CHOICES = [
        ('Manager', 'Manager'),
        ('Developer', 'Developer'),
        ('Designer', 'Designer'),
        ('HR', 'HR'),
        ('Accountant', 'Accountant'),
        ('Sales Executive', 'Sales Executive'),
        ('Marketing Executive', 'Marketing Executive'),
        ('Other', 'Other'),
    ]
    
    DEPARTMENT_CHOICES = [
        ('IT', 'IT'),
        ('HR', 'HR'),
        ('Finance', 'Finance'),
        ('Sales', 'Sales'),
        ('Marketing', 'Marketing'),
        ('Operations', 'Operations'),
        ('Other', 'Other'),
    ]
    
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()], unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    designation = models.CharField(max_length=50, choices=DESIGNATION_CHOICES)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    date_of_joining = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """
        Meta options for Employee model.
        """
        ordering = ['-created_at']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
    
    def __str__(self):
        """
        String representation of the Employee model.
        """
        return f"{self.name} ({self.employee_id})"
    
    def save(self, *args, **kwargs):
        """
        Override save method to auto-generate employee_id if not provided.
        """
        if not self.employee_id:
            # Generate employee ID: EMP + last 6 digits of pk
            last_employee = Employee.objects.order_by('-id').first()
            if last_employee and last_employee.employee_id:
                try:
                    last_num = int(last_employee.employee_id[3:])
                    new_num = last_num + 1
                except ValueError:
                    new_num = 1
            else:
                new_num = 1
            self.employee_id = f"EMP{new_num:06d}"
        super().save(*args, **kwargs)


class Attendance(models.Model):
    """
    Model representing employee attendance records.
    
    Attributes:
        employee: Foreign key to Employee model
        date: Date of attendance
        in_time: Time when employee checked in
        out_time: Time when employee checked out (optional)
        status: Attendance status (Present/Absent/Half Day)
        notes: Additional notes about attendance
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """
    
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Half Day', 'Half Day'),
        ('Leave', 'Leave'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    in_time = models.TimeField(null=True, blank=True)
    out_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Present')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """
        Meta options for Attendance model.
        """
        unique_together = ['employee', 'date']
        ordering = ['-date', '-in_time']
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'
    
    def __str__(self):
        """
        String representation of the Attendance model.
        """
        return f"{self.employee.name} - {self.date} ({self.status})"
    
    def calculate_work_hours(self):
        """
        Calculate total work hours based on in_time and out_time.
        
        Returns:
            float: Total work hours, or None if out_time is not set
        """
        if self.in_time and self.out_time:
            from datetime import datetime, date
            
            in_datetime = datetime.combine(self.date, self.in_time)
            out_datetime = datetime.combine(self.date, self.out_time)
            
            if out_datetime < in_datetime:
                # Handle case where out_time is next day
                from datetime import timedelta
                out_datetime += timedelta(days=1)
            
            time_delta = out_datetime - in_datetime
            hours = time_delta.total_seconds() / 3600
            return round(hours, 2)
        return None


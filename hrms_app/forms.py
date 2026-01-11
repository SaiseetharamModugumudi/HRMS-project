"""
Forms for HRMS application.
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import Employee, Attendance


class EmployeeForm(forms.ModelForm):
    """
    Form for creating and updating employee records.
    """
    
    class Meta:
        model = Employee
        fields = ['name', 'email', 'phone', 'address', 'designation', 'department', 'date_of_joining']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter address'
            }),
            'designation': forms.Select(attrs={
                'class': 'form-control'
            }),
            'department': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date_of_joining': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
    
    def clean_email(self):
        """
        Validate that email is unique.
        """
        email = self.cleaned_data.get('email')
        if email:
            # Check if this email already exists (exclude current instance if editing)
            existing_employee = Employee.objects.filter(email=email)
            if self.instance and self.instance.pk:
                existing_employee = existing_employee.exclude(pk=self.instance.pk)
            if existing_employee.exists():
                raise ValidationError('An employee with this email already exists.')
        return email
    
    def clean_phone(self):
        """
        Validate phone number format.
        """
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove any spaces, dashes, or parentheses
            phone_clean = ''.join(filter(str.isdigit, phone))
            if len(phone_clean) < 10:
                raise ValidationError('Phone number must be at least 10 digits.')
        return phone


class AttendanceForm(forms.ModelForm):
    """
    Form for marking employee attendance.
    """
    
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'in_time', 'out_time', 'status', 'notes']
        widgets = {
            'employee': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'in_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'out_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter any additional notes (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate employee dropdown with all employees (ordered by name)
        self.fields['employee'].queryset = Employee.objects.all().order_by('name')
        
        # Set default date to today
        from django.utils import timezone
        self.fields['date'].initial = timezone.now().date()


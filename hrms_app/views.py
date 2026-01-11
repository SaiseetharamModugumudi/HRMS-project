"""
Views for HRMS application.
Contains API endpoints and template-based views for employee management,
attendance tracking, and reporting.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib import messages
from datetime import datetime, date
import json as json_lib

from .models import Employee, Attendance
from .forms import EmployeeForm, AttendanceForm


def home(request):
    """
    Home page view displaying welcome message and list of employees.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered home page template with employee list
    """
    employees = Employee.objects.all()[:10]  # Show latest 10 employees
    total_employees = Employee.objects.count()
    return render(request, 'hrms_app/home.html', {
        'employees': employees,
        'total_employees': total_employees
    })


@require_http_methods(["GET", "POST"])
def api_employees(request):
    """
    API endpoint to add a new employee or retrieve list of all employees.
    
    GET: Returns JSON list of all employees
    POST: Creates a new employee with provided data
    
    Args:
        request: HTTP request object
        
    Returns:
        JsonResponse: Employee data or error message
    """
    if request.method == 'GET':
        """
        Retrieve all employees.
        
        Returns:
            JsonResponse: List of all employees with their details
        """
        employees = Employee.objects.all()
        employees_data = []
        for emp in employees:
            employees_data.append({
                'id': emp.id,
                'employee_id': emp.employee_id,
                'name': emp.name,
                'email': emp.email,
                'phone': emp.phone,
                'address': emp.address,
                'designation': emp.designation,
                'department': emp.department,
                'date_of_joining': emp.date_of_joining.strftime('%Y-%m-%d'),
                'created_at': emp.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })
        return JsonResponse({'employees': employees_data}, safe=False)
    
    elif request.method == 'POST':
        """
        Create a new employee.
        
        Expected POST data:
            - name: Employee name (required)
            - email: Email address (required, unique)
            - phone: Phone number (required)
            - address: Address (required)
            - designation: Job designation (required)
            - department: Department (required)
            - date_of_joining: Date in YYYY-MM-DD format (required)
            
        Returns:
            JsonResponse: Created employee data or error message
        """
        try:
            data = json_lib.loads(request.body) if request.body else request.POST
            
            # Validate required fields
            required_fields = ['name', 'email', 'phone', 'address', 'designation', 'department', 'date_of_joining']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
            
            # Parse date_of_joining
            try:
                date_of_joining = datetime.strptime(data['date_of_joining'], '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
            
            # Create employee
            employee = Employee.objects.create(
                name=data['name'],
                email=data['email'],
                phone=data['phone'],
                address=data['address'],
                designation=data['designation'],
                department=data['department'],
                date_of_joining=date_of_joining
            )
            
            return JsonResponse({
                'message': 'Employee created successfully',
                'employee': {
                    'id': employee.id,
                    'employee_id': employee.employee_id,
                    'name': employee.name,
                    'email': employee.email,
                    'phone': employee.phone,
                    'address': employee.address,
                    'designation': employee.designation,
                    'department': employee.department,
                    'date_of_joining': employee.date_of_joining.strftime('%Y-%m-%d'),
                }
            }, status=201)
            
        except json_lib.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


def api_employee_detail(request, employee_id):
    """
    API endpoint to retrieve details of a specific employee.
    
    Args:
        request: HTTP request object
        employee_id: ID or employee_id of the employee
        
    Returns:
        JsonResponse: Employee details with attendance records
    """
    try:
        # Try to get by primary key first, then by employee_id
        if employee_id.isdigit():
            employee = get_object_or_404(Employee, id=int(employee_id))
        else:
            employee = get_object_or_404(Employee, employee_id=employee_id)
        
        # Get recent attendance records
        attendances = Attendance.objects.filter(employee=employee).order_by('-date')[:30]
        attendance_data = []
        for att in attendances:
            attendance_data.append({
                'date': att.date.strftime('%Y-%m-%d'),
                'in_time': att.in_time.strftime('%H:%M:%S') if att.in_time else None,
                'out_time': att.out_time.strftime('%H:%M:%S') if att.out_time else None,
                'status': att.status,
                'work_hours': att.calculate_work_hours(),
                'notes': att.notes,
            })
        
        return JsonResponse({
            'employee': {
                'id': employee.id,
                'employee_id': employee.employee_id,
                'name': employee.name,
                'email': employee.email,
                'phone': employee.phone,
                'address': employee.address,
                'designation': employee.designation,
                'department': employee.department,
                'date_of_joining': employee.date_of_joining.strftime('%Y-%m-%d'),
            },
            'attendances': attendance_data
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)


@require_http_methods(["GET", "POST"])
def api_attendance(request):
    """
    API endpoint to mark attendance or retrieve attendance records.
    
    GET: Retrieve attendance records (optional: employee_id, date filters)
    POST: Mark attendance for a specific employee
    
    Args:
        request: HTTP request object
        
    Returns:
        JsonResponse: Attendance data or error message
    """
    if request.method == 'GET':
        """
        Retrieve attendance records with optional filters.
        
        Query parameters:
            - employee_id: Filter by employee ID
            - date: Filter by specific date (YYYY-MM-DD)
            - start_date: Filter from date (YYYY-MM-DD)
            - end_date: Filter to date (YYYY-MM-DD)
            
        Returns:
            JsonResponse: List of attendance records
        """
        employee_id = request.GET.get('employee_id')
        date_filter = request.GET.get('date')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        attendances = Attendance.objects.all()
        
        if employee_id:
            if employee_id.isdigit():
                attendances = attendances.filter(employee_id=int(employee_id))
            else:
                try:
                    emp = Employee.objects.get(employee_id=employee_id)
                    attendances = attendances.filter(employee=emp)
                except Employee.DoesNotExist:
                    return JsonResponse({'error': 'Employee not found'}, status=404)
        
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                attendances = attendances.filter(date=filter_date)
            except ValueError:
                return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                attendances = attendances.filter(date__gte=start)
            except ValueError:
                return JsonResponse({'error': 'Invalid start_date format. Use YYYY-MM-DD'}, status=400)
        
        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                attendances = attendances.filter(date__lte=end)
            except ValueError:
                return JsonResponse({'error': 'Invalid end_date format. Use YYYY-MM-DD'}, status=400)
        
        attendance_data = []
        for att in attendances.order_by('-date', '-in_time'):
            attendance_data.append({
                'id': att.id,
                'employee_id': att.employee.employee_id,
                'employee_name': att.employee.name,
                'date': att.date.strftime('%Y-%m-%d'),
                'in_time': att.in_time.strftime('%H:%M:%S') if att.in_time else None,
                'out_time': att.out_time.strftime('%H:%M:%S') if att.out_time else None,
                'status': att.status,
                'work_hours': att.calculate_work_hours(),
                'notes': att.notes,
            })
        
        return JsonResponse({'attendances': attendance_data}, safe=False)
    
    elif request.method == 'POST':
        """
        Mark attendance for an employee.
        
        Expected POST data:
            - employee_id: Employee ID or employee_id string (required)
            - date: Date in YYYY-MM-DD format (optional, defaults to today)
            - in_time: Check-in time in HH:MM:SS format (optional)
            - out_time: Check-out time in HH:MM:SS format (optional)
            - status: Attendance status (Present/Absent/Half Day/Leave, default: Present)
            - notes: Additional notes (optional)
            
        Returns:
            JsonResponse: Created/updated attendance record or error message
        """
        try:
            data = json_lib.loads(request.body) if request.body else request.POST
            
            if 'employee_id' not in data:
                return JsonResponse({'error': 'Missing required field: employee_id'}, status=400)
            
            # Get employee
            employee_id = data['employee_id']
            if employee_id.isdigit():
                employee = get_object_or_404(Employee, id=int(employee_id))
            else:
                employee = get_object_or_404(Employee, employee_id=employee_id)
            
            # Parse date (default to today if not provided)
            if 'date' in data:
                try:
                    att_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
                except ValueError:
                    return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
            else:
                att_date = timezone.now().date()
            
            # Parse times if provided
            in_time = None
            out_time = None
            
            if 'in_time' in data and data['in_time']:
                try:
                    in_time = datetime.strptime(data['in_time'], '%H:%M:%S').time()
                except ValueError:
                    try:
                        in_time = datetime.strptime(data['in_time'], '%H:%M').time()
                    except ValueError:
                        return JsonResponse({'error': 'Invalid in_time format. Use HH:MM:SS or HH:MM'}, status=400)
            
            if 'out_time' in data and data['out_time']:
                try:
                    out_time = datetime.strptime(data['out_time'], '%H:%M:%S').time()
                except ValueError:
                    try:
                        out_time = datetime.strptime(data['out_time'], '%H:%M').time()
                    except ValueError:
                        return JsonResponse({'error': 'Invalid out_time format. Use HH:MM:SS or HH:MM'}, status=400)
            
            status = data.get('status', 'Present')
            notes = data.get('notes', '')
            
            # Get or create attendance record
            attendance, created = Attendance.objects.get_or_create(
                employee=employee,
                date=att_date,
                defaults={
                    'in_time': in_time,
                    'out_time': out_time,
                    'status': status,
                    'notes': notes
                }
            )
            
            # Update if record already exists
            if not created:
                if in_time:
                    attendance.in_time = in_time
                if out_time:
                    attendance.out_time = out_time
                if status:
                    attendance.status = status
                if notes:
                    attendance.notes = notes
                attendance.save()
            
            return JsonResponse({
                'message': 'Attendance marked successfully',
                'attendance': {
                    'id': attendance.id,
                    'employee_id': attendance.employee.employee_id,
                    'employee_name': attendance.employee.name,
                    'date': attendance.date.strftime('%Y-%m-%d'),
                    'in_time': attendance.in_time.strftime('%H:%M:%S') if attendance.in_time else None,
                    'out_time': attendance.out_time.strftime('%H:%M:%S') if attendance.out_time else None,
                    'status': attendance.status,
                    'work_hours': attendance.calculate_work_hours(),
                    'notes': attendance.notes,
                }
            }, status=201 if created else 200)
            
        except json_lib.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


def employee_list(request):
    """
    View to display list of all employees on a page.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered employee list template
    """
    employees = Employee.objects.all()
    
    # Filter by department if provided
    department_filter = request.GET.get('department')
    if department_filter:
        employees = employees.filter(department=department_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        employees = employees.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(employee_id__icontains=search_query)
        )
    
    return render(request, 'hrms_app/employee_list.html', {
        'employees': employees,
        'departments': Employee.DEPARTMENT_CHOICES,
        'selected_department': department_filter,
        'search_query': search_query
    })


def employee_detail(request, employee_id):
    """
    View to display details of a specific employee with attendance records.
    
    Args:
        request: HTTP request object
        employee_id: ID or employee_id of the employee
        
    Returns:
        HttpResponse: Rendered employee detail template
    """
    try:
        if employee_id.isdigit():
            employee = get_object_or_404(Employee, id=int(employee_id))
        else:
            employee = get_object_or_404(Employee, employee_id=employee_id)
        
        # Get attendance records
        attendances = Attendance.objects.filter(employee=employee).order_by('-date')[:50]
        
        # Calculate statistics
        total_present = attendances.filter(status='Present').count()
        total_absent = attendances.filter(status='Absent').count()
        total_leave = attendances.filter(status='Leave').count()
        total_half_day = attendances.filter(status='Half Day').count()
        
        return render(request, 'hrms_app/employee_detail.html', {
            'employee': employee,
            'attendances': attendances,
            'total_present': total_present,
            'total_absent': total_absent,
            'total_leave': total_leave,
            'total_half_day': total_half_day,
        })
    except Exception as e:
        return render(request, 'hrms_app/error.html', {'error': str(e)}, status=404)


def reports(request):
    """
    View to display department-wise employee count report with charts.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered reports template with department statistics
    """
    # Get department-wise employee count
    department_stats = Employee.objects.values('department').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Prepare data for charts
    departments = [item['department'] for item in department_stats]
    counts = [item['count'] for item in department_stats]
    
    # Get designation-wise count
    designation_stats = Employee.objects.values('designation').annotate(
        count=Count('id')
    ).order_by('-count')
    
    designations = [item['designation'] for item in designation_stats]
    designation_counts = [item['count'] for item in designation_stats]
    
    # Overall statistics
    total_employees = Employee.objects.count()
    total_departments = Employee.objects.values('department').distinct().count()
    total_designations = Employee.objects.values('designation').distinct().count()
    
    return render(request, 'hrms_app/reports.html', {
        'department_stats': department_stats,
        'departments': departments,
        'counts': counts,
        'designation_stats': designation_stats,
        'designations': designations,
        'designation_counts': designation_counts,
        'total_employees': total_employees,
        'total_departments': total_departments,
        'total_designations': total_designations,
    })


def add_employee(request):
    """
    View to add a new employee using a form.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered employee form template or redirect after successful submission
    """
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Employee {employee.name} has been added successfully!')
            return redirect('hrms_app:employee_detail', employee_id=employee.id)
    else:
        form = EmployeeForm()
    
    return render(request, 'hrms_app/employee_form.html', {
        'form': form,
        'title': 'Add New Employee'
    })


def add_attendance(request):
    """
    View to mark attendance for an employee using a form.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered attendance form template or redirect after successful submission
    """
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save()
            messages.success(request, f'Attendance for {attendance.employee.name} on {attendance.date} has been marked successfully!')
            return redirect('hrms_app:employee_detail', employee_id=attendance.employee.id)
    else:
        form = AttendanceForm()
    
    return render(request, 'hrms_app/attendance_form.html', {
        'form': form,
        'title': 'Mark Attendance'
    })


# HRMS - Human Resource Management System

A comprehensive Django-based Human Resource Management System (HRMS) that provides employee management, attendance tracking, and reporting capabilities.

## Features

### Employee Management
- ✅ Create, view, and manage employee records
- ✅ Employee attributes: name, email, phone, address, designation, department, date of joining
- ✅ Auto-generated unique employee IDs
- ✅ Search and filter employees by department
- ✅ Employee detail pages with full information

### Attendance Tracking
- ✅ Mark attendance with in-time and out-time
- ✅ Track attendance status (Present, Absent, Half Day, Leave)
- ✅ Automatic work hours calculation
- ✅ View attendance history for each employee
- ✅ Attendance statistics on employee detail pages

### Reporting
- ✅ Department-wise employee count reports
- ✅ Designation-wise employee distribution
- ✅ Interactive charts (bar charts and pie charts) using Chart.js
- ✅ Summary statistics and percentages
- ✅ Table-based data representation

### API Endpoints
- ✅ RESTful API for employee management
- ✅ RESTful API for attendance tracking
- ✅ JSON responses for all API endpoints
- ✅ Error handling and validation

## Project Structure

```
hrms_project/
├── hrms_app/                  # Main application directory
│   ├── models.py              # Employee and Attendance models
│   ├── views.py               # API and template-based views
│   ├── urls.py                # URL routing configuration
│   ├── admin.py               # Django admin configuration
│   ├── templates/             # HTML templates
│   │   └── hrms_app/
│   │       ├── base.html      # Base template
│   │       ├── home.html      # Home page
│   │       ├── employee_list.html      # Employee listing page
│   │       ├── employee_detail.html    # Employee detail page
│   │       ├── reports.html   # Reports page with charts
│   │       └── error.html     # Error page
│   └── static/                # Static files (CSS, JS)
│       └── hrms_app/
│           └── css/
│               └── style.css  # Main stylesheet
├── hrms_project/              # Django project settings
│   ├── settings.py            # Project settings
│   ├── urls.py                # Main URL configuration
│   └── wsgi.py                # WSGI configuration
├── manage.py                  # Django management script
└── README.md                  # This file
```

## Requirements

- Python 3.8+
- Django 4.2+
- SQLite (default database, can be changed in settings)

## Installation and Setup

### 1. Clone or download the project

```bash
cd hrms_project_directory
```

### 2. Create a virtual environment (recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install django
```

Or create a `requirements.txt` file:
```
Django>=4.2
```

Then install:
```bash
pip install -r requirements.txt
```

### 4. Run database migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a superuser (optional, for admin access)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 6. Collect static files

```bash
python manage.py collectstatic --noinput
```

### 7. Run the development server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Usage

### Web Interface

1. **Home Page** (`/`)
   - Welcome message and quick statistics
   - Recent employees list
   - Quick action buttons
   - API endpoint information

2. **Employee List** (`/employees/`)
   - View all employees in a table format
   - Search employees by name, email, or ID
   - Filter by department
   - Click "View" to see employee details

3. **Employee Details** (`/employees/<employee_id>/`)
   - Complete employee information
   - Attendance statistics
   - Attendance history table

4. **Reports** (`/reports/`)
   - Department-wise employee count (bar chart)
   - Designation-wise distribution (pie chart)
   - Summary statistics
   - Data tables with percentages

5. **Admin Panel** (`/admin/`)
   - Full CRUD operations for employees and attendance
   - Use the superuser account created in setup step 5

### API Endpoints

#### Employee Management

**GET `/api/employees/`**
- Retrieve all employees
- Response: JSON array of employee objects

**POST `/api/employees/`**
- Create a new employee
- Required fields: `name`, `email`, `phone`, `address`, `designation`, `department`, `date_of_joining`
- Date format: `YYYY-MM-DD`
- Response: Created employee object

**Example POST request:**
```json
{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "1234567890",
    "address": "123 Main St, City, Country",
    "designation": "Developer",
    "department": "IT",
    "date_of_joining": "2024-01-15"
}
```

**GET `/api/employees/<employee_id>/`**
- Retrieve details of a specific employee
- Includes attendance records
- Response: Employee object with attendance array

#### Attendance Management

**GET `/api/attendance/`**
- Retrieve attendance records
- Query parameters:
  - `employee_id`: Filter by employee ID
  - `date`: Filter by specific date (YYYY-MM-DD)
  - `start_date`: Filter from date (YYYY-MM-DD)
  - `end_date`: Filter to date (YYYY-MM-DD)

**POST `/api/attendance/`**
- Mark attendance for an employee
- Required field: `employee_id`
- Optional fields: `date` (defaults to today), `in_time`, `out_time`, `status`, `notes`
- Time format: `HH:MM:SS` or `HH:MM`
- Response: Created/updated attendance object

**Example POST request:**
```json
{
    "employee_id": "EMP000001",
    "date": "2024-01-15",
    "in_time": "09:00:00",
    "out_time": "18:00:00",
    "status": "Present",
    "notes": "Regular working day"
}
```

## Models

### Employee Model
- `employee_id`: Auto-generated unique identifier (EMP000001 format)
- `name`: Full name
- `email`: Email address (unique)
- `phone`: Contact number
- `address`: Residential address
- `designation`: Job title (Manager, Developer, Designer, etc.)
- `department`: Department (IT, HR, Finance, Sales, etc.)
- `date_of_joining`: Date when employee joined
- `created_at`: Timestamp when record was created
- `updated_at`: Timestamp when record was last updated

### Attendance Model
- `employee`: Foreign key to Employee
- `date`: Date of attendance
- `in_time`: Check-in time
- `out_time`: Check-out time
- `status`: Attendance status (Present, Absent, Half Day, Leave)
- `notes`: Additional notes
- `created_at`: Timestamp when record was created
- `updated_at`: Timestamp when record was last updated

## Documentation

All functions and classes are documented with docstrings following Python documentation standards. Key documentation includes:

- Function purposes and parameters
- Return values and data formats
- Example usage for API endpoints
- Error handling information

## Development

### Running Tests

```bash
python manage.py test
```

### Database Reset

To reset the database:

```bash
python manage.py flush
python manage.py migrate
```

### Creating Migrations

After modifying models:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Technologies Used

- **Backend**: Django 4.2
- **Database**: SQLite (default)
- **Frontend**: HTML, CSS, JavaScript
- **Charts**: Chart.js (via CDN)
- **Styling**: Custom CSS with modern design principles

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

This project is provided as-is for educational and development purposes.

## Author

HRMS Development Team

## Support

For issues or questions, please refer to the Django documentation or contact the development team.

---

**Note**: This is a basic HRMS implementation. For production use, consider adding:
- User authentication and authorization
- Advanced security measures
- Database optimization
- Unit and integration tests
- Deployment configuration
- Logging and monitoring
- Backup and recovery procedures


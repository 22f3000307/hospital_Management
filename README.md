# Swasthub

A web-based hospital management system built with Flask and Jinja templates. Features a modern, minimalistic UI with green and grey theme colors.

## Features

### Admin
- Dashboard with overview statistics
- Manage doctors (Add, Edit, Delete)
- View patients and their details
- View all appointments

### Doctor
- Dashboard with appointment statistics
- View and manage appointments (Approve, Complete, Cancel)
- Add medical records for patients
- View patient list
- Update profile

### Patient
- Dashboard with appointment and records overview
- Browse available doctors
- Book appointments with preferred doctors
- View appointment history
- View medical records
- Update profile

## Technology Stack
- **Backend**: Flask (Python)
- **Frontend**: Jinja2 Templates with Font Awesome Icons
- **Database**: SQLite with SQLAlchemy ORM
- **Styling**: CSS with responsive design

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install flask flask-sqlalchemy werkzeug
```

3. Run the application:
```bash
python app.py
```

4. Access the application at `http://localhost:5000`

## Default Admin Credentials
- Username: admin
- Password: admin123

## Project Structure
```
swasthub/
├── app.py                 # Main application file
├── static/
│   └── style.css          # CSS styles
├── templates/
│   ├── base.html          # Base template
│   ├── home.html          # Homepage
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── admin/
│   │   ├── dash.html      # Admin dashboard
│   │   ├── docs.html      # Doctor list
│   │   ├── doc_form.html  # Add/Edit doctor
│   │   ├── pats.html      # Patient list
│   │   ├── pat_view.html  # Patient details
│   │   └── apts.html      # Appointment list
│   ├── doctor/
│   │   ├── dash.html      # Doctor dashboard
│   │   ├── apts.html      # Appointments
│   │   ├── pats.html      # Patients
│   │   ├── recs.html      # Medical records
│   │   ├── rec_form.html  # Add record
│   │   └── profile.html   # Profile
│   └── patient/
│       ├── dash.html      # Patient dashboard
│       ├── docs.html      # Find doctors
│       ├── apt_form.html  # Book appointment
│       ├── apts.html      # My appointments
│       ├── recs.html      # My records
│       └── profile.html   # Profile
└── README.md
```

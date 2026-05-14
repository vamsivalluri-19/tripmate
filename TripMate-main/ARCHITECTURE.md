# TripMate - Separated Frontend & Backend Architecture

## 📋 Overview

The TripMate application has been reorganized into a **clear separation of concerns**:

- **Backend**: Django application logic, database models, views, and forms
- **Frontend**: HTML templates, CSS styling, static assets, and media files

## 📁 Folder Organization

### Backend (`backend/`)
Contains all Django server-side code:
```
backend/
├── tourAndTravel/          # Django project settings & configuration
├── travelapp/              # Main Django application
├── manage.py              # Django management script
├── db.sqlite3             # Database file
└── requirements.txt       # Python dependencies
```

### Frontend (`frontend/`)
Contains all user interface and static assets:
```
frontend/
├── templates/             # HTML templates for all pages
├── static/               # CSS, JavaScript, and images
├── media/                # User-uploaded files
└── README.md             # Frontend documentation
```

## 🚀 Running the Application

### Step 1: Navigate to Backend

```bash
cd backend
```

### Step 2: Start Django Server

**Using the virtual environment:**
```bash
cd c:\Users\VAMSI VALLURI\Downloads\TripMate-main
.venv\Scripts\python.exe TripMate-main\backend\manage.py runserver 127.0.0.1:8000
```

**Or from inside backend folder:**
```bash
cd backend
..\..\..\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

### Step 3: Open in Browser

Navigate to: **http://127.0.0.1:8000/**

## 🔗 How Frontend & Backend Connect

### Path Configuration
Django settings have been updated to reference the new structure:

**In `backend/tourAndTravel/settings.py`:**
```python
PROJECT_ROOT = os.path.dirname(BASE_DIR)
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, 'frontend', 'templates')
STATICFILES_DIRS = (os.path.join(PROJECT_ROOT, 'frontend', 'static'),)
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'frontend', 'media')
```

This ensures:
- Templates load from `frontend/templates/`
- Static files load from `frontend/static/`
- Media uploads go to `frontend/media/`

### Request/Response Flow

```
User Browser
    ↓
Django URLs (backend/travelapp/urls.py)
    ↓
Django View (backend/travelapp/views.py)
    ↓
Database Query (backend/travelapp/models.py)
    ↓
Template Rendering (frontend/templates/)
    ↓
Static Assets (frontend/static/)
    ↓
User Browser (rendered HTML)
```

## 📚 Key Files by Function

### Authentication
- **Backend**: `backend/travelapp/views.py` → `registerView()`, `LoginView`
- **Frontend**: `frontend/templates/registration/login.html`, `register.html`

### Flight Search
- **Backend**: `backend/travelapp/views.py` → `FlightView()`
- **Backend**: `backend/travelapp/models.py` → `Flights` model
- **Frontend**: `frontend/templates/flights.html`

### Hotel Search
- **Backend**: `backend/travelapp/views.py` → `HotelView()`
- **Backend**: `backend/travelapp/models.py` → `Hotels` model
- **Frontend**: `frontend/templates/hotels.html`

### Package Booking
- **Backend**: `backend/travelapp/views.py` → `PackageView()`, `PackageBook()`
- **Frontend**: `frontend/templates/package.html`, `bookpackage.html`

### Dashboard
- **Backend**: `backend/travelapp/views.py` → `Dashboard()`
- **Frontend**: `frontend/templates/dashboard.html`

## 🔐 Security Features

All protected views have `@login_required` decorator:
- `/package/`
- `/flights/`
- `/hotels/`
- `/places/`
- `/accounts/profile/` (Dashboard)
- All booking and cancellation views

Unauthenticated users are redirected to `/accounts/login/`

## 📱 Responsive Design

The frontend uses **Bootstrap 4.4.1** for responsive layouts that work on:
- Desktop browsers
- Tablets
- Mobile devices

## 🎨 UI Components

### Base Template (`base.html`)
- Navigation bar with conditional menus
- Search forms
- Results display
- Footer with information

### Styling
- CSS files in `frontend/static/css/`
- Gradient backgrounds
- Box shadows
- Form styling
- Responsive grid layout

## 🔄 Development Workflow

### To modify a page:

1. **Check Backend Logic** → `backend/travelapp/views.py`
2. **Check Database Models** → `backend/travelapp/models.py`
3. **Edit Template** → `frontend/templates/page.html`
4. **Test in Browser** → Refresh and verify

### To add a new feature:

1. Add model in `backend/travelapp/models.py`
2. Create migration: `python manage.py makemigrations`
3. Apply migration: `python manage.py migrate`
4. Create view in `backend/travelapp/views.py`
5. Add URL in `backend/travelapp/urls.py`
6. Create template in `frontend/templates/`

## 📊 Project Statistics

- **Backend**: 1 project + 1 app + 7 models + 15 views
- **Frontend**: 1 base template + 13 page templates + 2 CSS files
- **Database**: SQLite with 6 main tables + booking tables
- **Authentication**: Django built-in with custom forms

## ✅ Verification Checklist

After restructuring, verify:
- [x] Backend folder contains all Django files
- [x] Frontend folder contains all templates and static files
- [x] Django settings updated with correct paths
- [x] `manage.py check` passes successfully
- [x] Database file exists in backend folder
- [x] Templates folder structure maintained
- [x] Static files (CSS, images) accessible
- [x] Server runs without errors

## 🆘 Troubleshooting

### Templates not found?
Check path in `backend/tourAndTravel/settings.py` → `TEMPLATE_DIR`

### Static files not loading?
Check `STATICFILES_DIRS` and `STATIC_ROOT` in settings.py

### Database not found?
Ensure `db.sqlite3` is in the `backend/` folder

### Server won't start?
Run `python manage.py check` from backend folder to diagnose issues

---

**Architecture**: Separated Frontend/Backend  
**Framework**: Django 5.2  
**Database**: SQLite3  
**Status**: ✅ Fully Restructured and Tested

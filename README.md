# TripMate

A simple travel booking demo (flights, hotels, packages) written with Django.

## Repo layout

- `TripMate-main/` — main project directory
  - `backend/` — Django backend (manage.py, app: `travelapp`)
  - `frontend/` — templates, static, media

This README contains quick setup steps to run the project locally.

## Prerequisites

- Python 3.11+
- Git
- (optional) virtualenv or venv

## Quick start (development)

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install backend requirements:

```powershell
pip install -r TripMate-main/backend/requirements.txt
```

3. Run migrations and seed example hotels:

```powershell
cd TripMate-main/backend
python manage.py migrate
python manage.py seed_hotels
```

4. Create a superuser (optional):

```powershell
python manage.py createsuperuser
```

5. Start the dev server:

```powershell
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

## Tests

Run Django tests:

```powershell
cd TripMate-main/backend
python manage.py test
```

## Notes

- The main Django project files live in `TripMate-main/backend` and the database file is `TripMate-main/backend/db.sqlite3` by default.
- There are existing README files inside `TripMate-main/`, `TripMate-main/backend/`, and `TripMate-main/frontend/` with more details.

If you want, I can add CI, a CONTRIBUTING guide, or publish the project to a hosting service.

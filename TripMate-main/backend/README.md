# Backend - Django Application

This folder contains all backend code for the TripMate travel and booking application.

## Structure

```
backend/
├── manage.py                  # Django management script
├── db.sqlite3                 # SQLite database
├── requirements.txt           # Python dependencies
├── tourAndTravel/             # Django project settings
│   ├── settings.py           # Main Django configuration
│   ├── urls.py               # URL routing
│   ├── wsgi.py               # WSGI configuration
│   └── asgi.py               # ASGI configuration
└── travelapp/                 # Main Django app
    ├── models.py             # Database models (Flights, Hotels, Famous, Bookings)
    ├── views.py              # View logic (search, book, cancel operations)
    ├── forms.py              # Form definitions (SignUp, Search, Booking forms)
    ├── urls.py               # App URL patterns
    ├── admin.py              # Admin interface configuration
    └── migrations/           # Database migration files
```

## Running the Backend

### From the root project directory:

```bash
cd backend
python manage.py runserver 127.0.0.1:8000
```

Or use the virtual environment:
```bash
..\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

## Key Features

- **Authentication**: User registration, login, and logout
- **Flight Search**: Search flights by source, destination, and date
- **Hotel Search**: Search hotels by city and date
- **Package Booking**: Combined flight + hotel package bookings
- **Dashboard**: View user's booked flights, hotels, and packages
- **Cancellation**: Cancel existing bookings

## Database Models

- `User`: Django built-in user model
- `City`: Cities with location information
- `Flights`: Flight information with company, timings, and pricing
- `Hotels`: Hotel details with ratings and amenities
- `Famous`: Famous places to visit
- `BookFlight`: User's flight bookings
- `BookHotel`: User's hotel bookings
- `BookPackage`: User's package bookings

## API Endpoints

- `/` - Home page
- `/register/` - User registration
- `/accounts/login/` - User login
- `/logout/` - User logout
- `/package/` - Package search and booking
- `/flights/` - Flight search and booking
- `/hotels/` - Hotel search and booking
- `/places/` - Famous places
- `/accounts/profile/` - User dashboard

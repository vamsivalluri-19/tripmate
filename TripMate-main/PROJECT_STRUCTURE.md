# TripMate - Travel and Tour Booking Application

A Django-based web application for booking flights, hotels, and travel packages.

## 📁 Project Structure

The project is now organized into **Frontend** and **Backend** for better separation of concerns:

```
TripMate-main/
├── frontend/                      # Frontend (UI/UX)
│   ├── templates/                 # Django HTML templates
│   │   ├── base.html             # Base template with navbar
│   │   ├── index.html            # Home page
│   │   ├── flights.html          # Flight search
│   │   ├── hotels.html           # Hotel search
│   │   ├── package.html          # Package booking
│   │   ├── places.html           # Famous places
│   │   ├── dashboard.html        # User dashboard
│   │   ├── booking pages/        # Flight/Hotel/Package confirmations
│   │   └── registration/         # Login and register pages
│   ├── static/                    # CSS, JS, Images
│   │   ├── css/                  # Stylesheets
│   │   └── img/                  # Static images
│   ├── media/                     # User uploads (hotel images, etc.)
│   └── README.md                  # Frontend documentation
│
├── backend/                       # Backend (Business Logic)
│   ├── manage.py                 # Django management
│   ├── db.sqlite3                # Database
│   ├── requirements.txt          # Python dependencies
│   ├── tourAndTravel/            # Django project config
│   │   ├── settings.py           # Configuration (updated paths)
│   │   ├── urls.py               # URL routing
│   │   ├── wsgi.py               # WSGI server config
│   │   └── asgi.py               # ASGI server config
│   ├── travelapp/                # Main Django app
│   │   ├── models.py             # Database models
│   │   ├── views.py              # View logic
│   │   ├── forms.py              # Form definitions
│   │   ├── urls.py               # URL patterns
│   │   ├── admin.py              # Admin config
│   │   └── migrations/           # Database migrations
│   └── README.md                  # Backend documentation
│
├── .venv/                         # Virtual environment
├── README.md                       # Main documentation (this file)
└── screenshots/                    # Project screenshots
```

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

### 2. Access the Application

Open your browser and navigate to:
```
http://127.0.0.1:8000/
```

## 🔑 Key Features

### User Management
- User registration with custom password
- Secure login/logout
- Persistent user sessions

### Flight Booking
- Search flights by source, destination, date
- View available seats
- Book individual seats
- Cancel bookings from dashboard

### Hotel Booking
- Search hotels by city and date
- View available rooms
- Book rooms
- Cancel bookings from dashboard

### Package Booking
- Search combined flight + hotel packages
- View famous places in destination
- Book complete packages
- Manage all bookings in one dashboard

### Dashboard
- View all booked flights
- View all booked hotels
- View all booked packages
- Cancel any booking directly from dashboard

## 📊 Database Models

### Core Models
- **User**: Django user model for authentication
- **City**: Cities with location information
- **Flights**: Flight data (source, destination, company, price, seats, timing)
- **Hotels**: Hotel data (name, address, price, rooms, amenities, rating)
- **Famous**: Famous places to visit in each city

### Booking Models
- **BookFlight**: Stores user flight bookings
- **BookHotel**: Stores user hotel bookings
- **BookPackage**: Stores user package bookings (flight + hotel combined)

## 🔄 Frontend-Backend Connection

The frontend communicates with the backend through:

1. **URL Routing**: Django's `{% url %}` template tag generates links
2. **Forms**: Django forms handle user input (search, login, booking)
3. **Template Context**: Backend passes querysets to templates for rendering
4. **Authentication**: Django's login_required decorator protects views
5. **Sessions**: User session management for persistent login

### Request Flow Example (Flight Search):
```
User enters search → flights.html form (POST)
→ FlightView.POST() → Query database
→ Render flights.html with results
→ User clicks flight → bookflight view
→ Display booking form → User confirms
→ Save BookFlight record → Redirect to dashboard
```

## 🛠️ Technologies Used

### Backend
- **Django 5.2**: Web framework
- **SQLite3**: Database
- **Python 3.x**: Programming language

### Frontend
- **HTML5**: Markup
- **CSS3**: Styling with gradients and animations
- **Bootstrap 4.4.1**: Responsive framework
- **Django Templates**: Server-side rendering

## 📝 Important Notes

- The app now has separated frontend and backend folders
- Settings.py has been updated to reference the new paths
- Template paths: `../frontend/templates/`
- Static files path: `../frontend/static/`
- Media path: `../frontend/media/`
- Run the server from the `backend/` folder

## 🔗 URL Patterns

| Route | Purpose |
|-------|---------|
| `/` | Home page |
| `/register/` | User registration |
| `/accounts/login/` | User login |
| `/logout/` | Logout |
| `/package/` | Package search & booking |
| `/flights/` | Flight search & booking |
| `/hotels/` | Hotel search & booking |
| `/places/` | Famous places |
| `/accounts/profile/` | Dashboard |

## 📚 Documentation

- See [backend/README.md](backend/README.md) for backend documentation
- See [frontend/README.md](frontend/README.md) for frontend documentation

---

**Created by**: Guru Patil  
**Project**: Travel Trip - A Django Tour and Travel Booking Application

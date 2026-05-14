# Frontend - User Interface

This folder contains all frontend code for the TripMate travel and booking application.

## Structure

```
frontend/
├── templates/                 # Django HTML templates
│   ├── base.html             # Base template with navbar and footer
│   ├── index.html            # Home page
│   ├── flights.html          # Flight search and display
│   ├── hotels.html           # Hotel search and display
│   ├── package.html          # Package search combining flights + hotels
│   ├── places.html           # Famous places listing
│   ├── dashboard.html        # User dashboard (bookings management)
│   ├── bookflight.html       # Flight booking confirmation
│   ├── bookhotel.html        # Hotel booking confirmation
│   ├── bookpackage.html      # Package booking confirmation
│   ├── cancelflight.html     # Flight cancellation page
│   ├── cancelhotel.html      # Hotel cancellation page
│   ├── cancelpackage.html    # Package cancellation page
│   └── registration/
│       ├── login.html        # User login page
│       └── register.html     # User registration page
├── static/                    # Static files (CSS, JS, Images)
│   ├── css/
│   │   ├── style.css         # Main stylesheet
│   │   └── styleone.css      # Additional styles
│   └── img/                  # Static images (logo, icons)
└── media/                     # User-uploaded media
    └── img/                  # Hotel and place images
```

## Key Features

### Pages
- **Home (index.html)**: Landing page with navigation to main sections
- **Login/Register**: User authentication pages
- **Flight Search**: Search flights by source, destination, date
- **Hotel Search**: Search hotels by city and date
- **Package Search**: Combined search for flights + hotels with famous places
- **Dashboard**: Manage all bookings (view, cancel)
- **Booking Pages**: Confirmation pages for selecting seats/rooms

### Styling
- Bootstrap 4.4.1 for responsive layout
- Custom CSS for design and animations
- Gradient backgrounds and shadow effects

### Components
- Navigation bar with conditional authenticated/non-authenticated menus
- Search forms with date picker
- Flight/Hotel cards with booking options
- Booking tables in dashboard
- Footer with copyright and links

## Template Tags Used

- `{% url %}` - Generate URLs from named routes
- `{% for %}` - Loop through querysets
- `{% if %}` - Conditional rendering
- `{% load static %}` - Load static files
- `{% csrf_token %}` - CSRF protection for forms
- `{{ }}` - Display variables

## Static Files

### CSS
- Bootstrap framework integration
- Responsive design
- Gradient backgrounds
- Form styling
- Button and card styling

### Images
- Logo and icons
- Travel-related images
- Hotel pictures (loaded from media folder)
- Place images (loaded from media folder)

## Development Notes

- All templates extend `base.html` for consistency
- Forms are rendered using Django form rendering: `{{ form.as_p }}`
- URL generation uses Django's `{% url %}` tag for dynamic links
- Media files are served from the `/media/` endpoint
- Static files are served from the `/static/` endpoint

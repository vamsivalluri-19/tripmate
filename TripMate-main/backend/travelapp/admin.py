from django.contrib import admin
from travelapp.models import (Flights, Famous, Hotels, City, BookFlight, BookHotel, BookPackage,
                              UserProfile, FlightReview, HotelReview, Wishlist, Discount,
                              Invoice, Notification, SearchHistory, Payment)

# Register your models here.
admin.site.register(Flights)
admin.site.register(Famous)
admin.site.register(Hotels)
admin.site.register(City)
admin.site.register(BookFlight)
admin.site.register(BookHotel)
admin.site.register(BookPackage)

# New Feature Models
admin.site.register(UserProfile)
admin.site.register(FlightReview)
admin.site.register(HotelReview)
admin.site.register(Wishlist)
admin.site.register(Discount)
admin.site.register(Invoice)
admin.site.register(Notification)
admin.site.register(SearchHistory)
admin.site.register(Payment)

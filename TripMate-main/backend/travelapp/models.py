from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# Create your models here.
class City(models.Model):
    city = models.CharField(max_length=200)
    bestlink = models.CharField(max_length=200)
    weekgetlinks = models.CharField(max_length=200)

    def __str__(self):
        return self.city


class Flights(models.Model):
    id = models.AutoField(primary_key=True)
    source = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    flight_num = models.CharField(max_length=10)
    city = models.ForeignKey(City,on_delete=models.CASCADE)
    eprice = models.IntegerField(null=True)
    dept_time = models.TimeField(auto_now=False,auto_now_add=False)
    dest_time = models.TimeField(auto_now=False,auto_now_add=False)
    company = models.CharField(max_length=15,default=" ")
    seats = models.IntegerField()
    stations = models.TextField(null=True, blank=True, help_text="Comma-separated list of stations/waypoints including start and end")
    avg_rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])


    def __str__(self):
        return self.flight_num

    @property
    def stations_list(self):
        if not self.stations:
            return []
        return [s.strip() for s in self.stations.split(',') if s.strip()]

class Hotels(models.Model):
    id = models.AutoField(primary_key=True)
    city = models.ForeignKey(City,on_delete=models.CASCADE)
    hotel_name = models.CharField(max_length=200)
    hotel_address = models.CharField(max_length=500)
    hotel_price = models.IntegerField(null=True)
    hotel_rating = models.IntegerField(null=True)
    amenities = models.CharField(max_length=500)
    distfromap = models.IntegerField(null=True)
    rooms = models.IntegerField(default=0)
    image1 = models.ImageField(null=True,upload_to='img/')
    avg_rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])


    def __str__(self):
        return self.hotel_name

class Famous(models.Model):
    city = models.ForeignKey(City,on_delete=models.CASCADE)
    place_name = models.CharField(max_length=200)
    image = models.ImageField(null=True,upload_to='img/')
    desc = models.CharField(max_length=500)

    def __str__(self):
        return self.place_name

class BookFlight(models.Model):
    BOOKING_STATUS = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    username_id = models.ForeignKey(User,on_delete=models.CASCADE)
    flight = models.CharField(max_length=10)
    date = models.CharField(max_length=20)
    seat = models.IntegerField(default=1)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='confirmed')
    has_insurance = models.BooleanField(default=False)
    insurance_cost = models.IntegerField(default=0)
    total_price = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.flight} - {self.date}"

class BookHotel(models.Model):
    BOOKING_STATUS = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    ROOM_TYPES = [
        ('single', 'Single Room'),
        ('double', 'Double Room'),
        ('deluxe', 'Deluxe Room'),
        ('suite', 'Suite'),
        ('family', 'Family Room'),
    ]
    username_id = models.ForeignKey(User,on_delete=models.CASCADE)
    hotel_name = models.CharField(max_length=100)
    date = models.CharField(max_length=20)
    checkout_date = models.CharField(max_length=20, null=True, blank=True)
    room = models.IntegerField(default=1)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='double', null=True, blank=True)
    guest_count = models.IntegerField(default=2, null=True, blank=True)
    has_breakfast = models.BooleanField(default=False)
    breakfast_cost = models.IntegerField(default=0)
    special_requests = models.TextField(null=True, blank=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='confirmed')
    has_insurance = models.BooleanField(default=False)
    insurance_cost = models.IntegerField(default=0)
    total_price = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.hotel_name} - {self.date}"

class BookPackage(models.Model):
    BOOKING_STATUS = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    username_id = models.ForeignKey(User,on_delete=models.CASCADE)
    seat = models.IntegerField(default=1)
    flight = models.CharField(max_length=10)
    hotel_name = models.CharField(max_length=10)
    room = models.IntegerField(default=1)
    date = models.CharField(max_length=20)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='confirmed')
    has_insurance = models.BooleanField(default=False)
    insurance_cost = models.IntegerField(default=0)
    total_price = models.IntegerField(default=0)

    def __str__(self):
        return f"Package - {self.date}"


# NEW FEATURES MODELS

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=500, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    profile_pic = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(blank=True)
    loyalty_points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class FlightReview(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flights, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    helpful_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Review by {self.user.username} for Flight {self.flight.flight_num}"

    class Meta:
        unique_together = ('user', 'flight')


class HotelReview(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotels, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    helpful_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Review by {self.user.username} for Hotel {self.hotel.hotel_name}"

    class Meta:
        unique_together = ('user', 'hotel')


class Wishlist(models.Model):
    ITEM_TYPE_CHOICES = [
        ('flight', 'Flight'),
        ('hotel', 'Hotel'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES)
    flight = models.ForeignKey(Flights, on_delete=models.CASCADE, null=True, blank=True)
    hotel = models.ForeignKey(Hotels, on_delete=models.CASCADE, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.item_type}"

    class Meta:
        unique_together = ('user', 'item_type', 'flight', 'hotel')


class Discount(models.Model):
    code = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=500)
    discount_type = models.CharField(max_length=10, choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')])
    discount_value = models.IntegerField()
    min_booking_amount = models.IntegerField(default=0)
    max_usage = models.IntegerField(default=-1)
    usage_count = models.IntegerField(default=0)
    valid_from = models.DateField()
    valid_till = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        from django.utils.timezone import now
        today = now().date()
        return self.is_active and today >= self.valid_from and today <= self.valid_till

    def can_use(self):
        return self.is_valid() and (self.max_usage == -1 or self.usage_count < self.max_usage)


class Invoice(models.Model):
    BOOKING_TYPE_CHOICES = [
        ('flight', 'Flight'),
        ('hotel', 'Hotel'),
        ('package', 'Package'),
    ]
    invoice_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking_type = models.CharField(max_length=10, choices=BOOKING_TYPE_CHOICES)
    booking_flight = models.ForeignKey(BookFlight, on_delete=models.SET_NULL, null=True, blank=True)
    booking_hotel = models.ForeignKey(BookHotel, on_delete=models.SET_NULL, null=True, blank=True)
    booking_package = models.ForeignKey(BookPackage, on_delete=models.SET_NULL, null=True, blank=True)
    subtotal = models.IntegerField()
    discount_amount = models.IntegerField(default=0)
    tax = models.IntegerField(default=0)
    total_amount = models.IntegerField()
    discount_code = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending')
    issued_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()

    def __str__(self):
        return self.invoice_number


class Notification(models.Model):
    NOTIFICATION_TYPE = [
        ('booking_confirmed', 'Booking Confirmed'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('booking_reminder', 'Booking Reminder'),
        ('review_request', 'Review Request'),
        ('special_offer', 'Special Offer'),
        ('system', 'System Message'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.notification_type} - {self.user.username}"

    class Meta:
        ordering = ['-created_at']


class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    search_type = models.CharField(max_length=10, choices=[('flight', 'Flight'), ('hotel', 'Hotel'), ('package', 'Package')])
    source = models.CharField(max_length=200, blank=True)
    destination = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    search_date = models.DateTimeField(auto_now_add=True)
    result_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.search_type}"

    class Meta:
        ordering = ['-search_date']


class Payment(models.Model):
    PAYMENT_METHOD = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('net_banking', 'Net Banking'),
        ('upi', 'UPI'),
        ('wallet', 'Wallet'),
    ]
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.status}"

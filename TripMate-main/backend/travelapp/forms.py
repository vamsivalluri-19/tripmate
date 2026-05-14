from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from .models import (Flights, Hotels, BookPackage, BookFlight, BookHotel, Famous,
                     UserProfile, FlightReview, HotelReview, Wishlist, Discount, Invoice, Payment)
from django.core.exceptions import ValidationError
import datetime


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30,widget= forms.TextInput(attrs={'class':'d-form form-control'}))
    last_name = forms.CharField(max_length=30,widget= forms.TextInput(attrs={'class':'d-form form-control'}))
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.',widget= forms.TextInput(attrs={'class':'d-form form-control'}))
    username = forms.CharField(max_length=254,widget= forms.TextInput(attrs={'class':'d-form form-control'}))
    password1=forms.CharField(max_length=20,widget=forms.PasswordInput(attrs={'class':'d-form form-control'}))
    password2=forms.CharField(max_length=20,widget=forms.PasswordInput(attrs={'class':'d-form form-control'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError(
                "password and confirm_password does not match"
            )

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254,widget= forms.TextInput(attrs={'class':'d-form form-control'}))
    password = forms.CharField(max_length=20,widget=forms.PasswordInput(attrs={'class':'d-form form-control'}))

    class Meta:
        model = User

class FlightForm(forms.Form):
    source = forms.ChoiceField(
        choices=(),
        label='SOURCE',
        widget=forms.Select(attrs={'class': 'fs-form form-control'}),
        required=False,
    )
    destination = forms.ChoiceField(
        choices=(),
        label='DESTINATION',
        widget=forms.Select(attrs={'class': 'fds-forms form-control'}),
        required=False,
    )
    date = forms.DateField(
        initial=datetime.date.today,
        label='DATE',
        widget=forms.DateInput(attrs={'class': 'fd-form form-control', 'type': 'date'}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        source_choices = kwargs.pop('source_choices', ())
        destination_choices = kwargs.pop('destination_choices', ())
        super().__init__(*args, **kwargs)
        self.fields['source'].choices = [('', 'Select source')] + [(item, item) for item in source_choices]
        self.fields['destination'].choices = [('', 'Select destination')] + [(item, item) for item in destination_choices]

    class Meta:
        model = Flights
        fields = ('source','destination','city')


class HotelForm(forms.Form):
    city = forms.ChoiceField(
        choices=(),
        label='CITY',
        widget=forms.Select(attrs={'class': 'fs-form form-control'}),
        required=False,
    )
    date = forms.DateField(
        initial=datetime.date.today,
        label='Date ',
        widget=forms.DateInput(attrs={'class': 'fd-form form-control', 'type': 'date'}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        city_choices = kwargs.pop('city_choices', ())
        super().__init__(*args, **kwargs)
        self.fields['city'].choices = [('', 'Select city')] + [(item, item) for item in city_choices]

    class Meta:
        model = Hotels
        fields = ('city')


class HotelCreateForm(forms.ModelForm):
    class Meta:
        model = Hotels
        fields = ['city', 'hotel_name', 'hotel_address', 'hotel_price', 'hotel_rating', 'amenities', 'distfromap', 'rooms', 'image1']
        widgets = {
            'hotel_name': forms.TextInput(attrs={'class': 'form-control'}),
            'hotel_address': forms.TextInput(attrs={'class': 'form-control'}),
            'hotel_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'hotel_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 5}),
            'amenities': forms.TextInput(attrs={'class': 'form-control'}),
            'distfromap': forms.NumberInput(attrs={'class': 'form-control'}),
            'rooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'image1': forms.ClearableFileInput(attrs={'class': 'form-control-file'})
        }

    def clean_hotel_name(self):
        name = self.cleaned_data.get('hotel_name')
        if Hotels.objects.filter(hotel_name__iexact=name).exists():
            raise ValidationError('A hotel with this name already exists.')
        return name
class ChoiceForm(forms.Form):
    flight = forms.CharField(max_length=20,widget=forms.TextInput(attrs={'class' : 'fs-form form-control','placeholder':'Choose Flight'}),required=False)
    seats = forms.IntegerField(widget=forms.TextInput(attrs={'class' : 'fs-form form-control','placeholder':'SEATS'}),required=False)
    hotel = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'class' : 'fs-form form-control','placeholder':'Choose Hotel'}),required=False)
    rooms = forms.IntegerField(widget=forms.TextInput(attrs={'class' : 'fs-form form-control','placeholder':'ROOMS'}),required=False)

    class Meta:
        models = BookPackage
        fields = ('flight','seat','hotel_name','room')

class SeatForm(forms.Form):
    seats = forms.IntegerField(widget=forms.TextInput(attrs={'class' : 'fs-form form-control','placeholder':'SEATS'}),required=False)

    class Meta:
        models = BookFlight
        fields = ('seats')

class RoomForm(forms.Form):
    rooms = forms.IntegerField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter number of rooms',
            'type': 'number',
            'min': '1'
        }),
        required=True,
        label='Number of Rooms'
    )

    class Meta:
        models = BookHotel
        fields = ('room')

class HotelBookingDetailsForm(forms.ModelForm):
    checkout_date = forms.DateField(
        label='Check-out Date',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        required=True
    )
    
    guest_count = forms.IntegerField(
        label='Number of Guests',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'number',
            'min': '1',
            'max': '10'
        }),
        required=True,
        initial=2
    )
    
    has_breakfast = forms.BooleanField(
        label='Include Breakfast?',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False
    )
    
    special_requests = forms.CharField(
        label='Special Requests',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Any special requests? (High floor, late check-in, extra bed, etc.)',
            'rows': 4
        }),
        required=False
    )

    class Meta:
        model = BookHotel
        fields = ('room_type', 'checkout_date', 'guest_count', 'has_breakfast', 'special_requests')
        widgets = {
            'room_type': forms.Select(attrs={'class': 'form-control'}),
        }

class CityForm(forms.Form):
    city = forms.ChoiceField(
        choices=(),
        label='CITY',
        widget=forms.Select(attrs={'class': 'fs-form form-control'}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        city_choices = kwargs.pop('city_choices', ())
        super().__init__(*args, **kwargs)
        self.fields['city'].choices = [('', 'Select city')] + [(item, item) for item in city_choices]

    class Meta:
        models = Famous


# NEW FEATURE FORMS

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('phone', 'address', 'city', 'country', 'profile_pic', 'bio')
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'profile_pic': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Bio', 'rows': 4}),
        }


class FlightReviewForm(forms.ModelForm):
    class Meta:
        model = FlightReview
        fields = ('rating', 'comment')
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Share your experience...', 'rows': 4}),
        }


class HotelReviewForm(forms.ModelForm):
    class Meta:
        model = HotelReview
        fields = ('rating', 'comment')
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Share your experience...', 'rows': 4}),
        }


class DiscountCodeForm(forms.Form):
    code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter discount code'
        })
    )


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ('payment_method',)
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }


class SearchFilterForm(forms.Form):
    PRICE_RANGE = [
        ('0-5000', '₹0 - ₹5,000'),
        ('5000-10000', '₹5,000 - ₹10,000'),
        ('10000-15000', '₹10,000 - ₹15,000'),
        ('15000-0', '₹15,000+'),
    ]
    RATING_RANGE = [
        ('4-5', '4★ - 5★ (Excellent)'),
        ('3-4', '3★ - 4★ (Good)'),
        ('2-3', '2★ - 3★ (Average)'),
    ]
    
    price_range = forms.ChoiceField(choices=PRICE_RANGE, required=False, widget=forms.RadioSelect())
    rating = forms.ChoiceField(choices=RATING_RANGE, required=False, widget=forms.RadioSelect())
    sort_by = forms.ChoiceField(
        choices=[
            ('price_low', 'Price: Low to High'),
            ('price_high', 'Price: High to Low'),
            ('rating', 'Highest Rated'),
            ('dept_early', 'Departure: Early First'),
            ('dept_late', 'Departure: Late First'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    max_price = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max budget (INR)'})
    )
    airline = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Airline (e.g. Air India)'})
    )


class BookingInvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ('discount_code',)
        widgets = {
            'discount_code': forms.Select(attrs={'class': 'form-control'}),
        }

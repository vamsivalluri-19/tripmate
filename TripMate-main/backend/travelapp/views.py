from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from .forms import HotelCreateForm
from django.db.models import Avg, Q, Sum
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .forms import (SignUpForm, HotelForm, FlightForm, ChoiceForm, SeatForm, RoomForm, CityForm,
                   UserProfileForm, FlightReviewForm, HotelReviewForm, DiscountCodeForm, PaymentForm,
                   SearchFilterForm, HotelBookingDetailsForm)
from .models import (Flights, Hotels, Famous, BookFlight, BookHotel, BookPackage, City,
                    UserProfile, FlightReview, HotelReview, Wishlist, Discount, Invoice,
                    Notification, SearchHistory, Payment)
from .airports import get_airport_info

# Create your views here.


def _flight_route_options():
    sources = Flights.objects.values_list('source', flat=True).distinct().order_by('source')
    destinations = Flights.objects.values_list('destination', flat=True).distinct().order_by('destination')
    return list(sources), list(destinations)


def _city_options():
    return list(City.objects.values_list('city', flat=True).distinct().order_by('city'))


def _remaining_flight_seats(flight_num, date):
    flight_obj = Flights.objects.filter(flight_num=flight_num).first()
    if not flight_obj:
        return None, None

    booked_seats = (
        BookFlight.objects.filter(flight=flight_obj.flight_num, date=date, status='confirmed').aggregate(total=Sum('seat'))['total'] or 0
    ) + (
        BookPackage.objects.filter(flight=flight_obj.flight_num, date=date, status='confirmed').aggregate(total=Sum('seat'))['total'] or 0
    )
    return max(flight_obj.seats - booked_seats, 0), flight_obj


def _remaining_hotel_rooms(hotel_name, date):
    # Resolve hotel_name which may be: hotel id (int), exact name, URL-encoded, hyphen-slug, or partial name
    hotel_obj = None
    from urllib.parse import unquote_plus

    # If already a Hotels instance
    if isinstance(hotel_name, Hotels):
        hotel_obj = hotel_name
    else:
        raw = hotel_name or ''
        raw = unquote_plus(str(raw)).strip()
        # try numeric id
        if raw.isdigit():
            hotel_obj = Hotels.objects.filter(id=int(raw)).first()
        # exact match
        if not hotel_obj:
            hotel_obj = Hotels.objects.filter(hotel_name__iexact=raw).first()
        # try replacing hyphens with spaces
        if not hotel_obj and '-' in raw:
            hotel_obj = Hotels.objects.filter(hotel_name__iexact=raw.replace('-', ' ')).first()
        # partial case-insensitive match
        if not hotel_obj:
            hotel_obj = Hotels.objects.filter(hotel_name__icontains=raw).first()

    if not hotel_obj:
        return None, None

    booked_rooms = (
        BookHotel.objects.filter(hotel_name=hotel_obj.hotel_name, date=date, status='confirmed').aggregate(total=Sum('room'))['total'] or 0
    ) + (
        BookPackage.objects.filter(hotel_name=hotel_obj.hotel_name, date=date, status='confirmed').aggregate(total=Sum('room'))['total'] or 0
    )
    return max(hotel_obj.rooms - booked_rooms, 0), hotel_obj

def IndexView(request):
    return render(request,'index.html')

@login_required
def PackageView(request):
    source_choices, destination_choices = _flight_route_options()
    if request.method=="POST":
        form = FlightForm(request.POST, source_choices=source_choices, destination_choices=destination_choices)
        if form.is_valid():
            source = form.cleaned_data['source'].strip() if form.cleaned_data['source'] else ''
            date = form.cleaned_data['date']
            destination = form.cleaned_data['destination'].strip() if form.cleaned_data['destination'] else ''
            # city = destination
            flights = Flights.objects.filter(
                source__icontains=source
            ).filter(
                destination__icontains=destination
            ) if source and destination else Flights.objects.none()
            
            famplace = Famous.objects.filter(city__city__icontains=destination)
            hotels = Hotels.objects.filter(city__city__icontains=destination)
            # Safely get a City instance or fallback to a string so templates/URLs don't break
            hotel_obj = hotels.first()
            if hotel_obj:
                j = hotel_obj.city
            else:
                city_obj = City.objects.filter(city__icontains=destination).first()
                if city_obj:
                    j = city_obj
                else:
                    j = destination
            # Make sure `city_value` is a plain string for URLs/templates
            if hasattr(j, 'city'):
                city_value = j.city
            else:
                city_value = str(j)
            s = {'source': source}
            c = {'city': city_value}
            f = {'Flights':flights}
            d = {'date':date}
            h = {'Hotels':hotels}
            fp = {'Famplace':famplace}
            form_dict = {'form': form}
            form1 = {'form1':form}
            no_results = not (flights.exists() or hotels.exists() or famplace.exists())
            nr = {'no_results': no_results}
            response = {**f,**s,**h,**fp,**form_dict,**d,**c,**nr}
            return render(request,'package.html',response)
        else:
            return render(request,'package.html',{'form': form})
    else:
        form = FlightForm(source_choices=source_choices, destination_choices=destination_choices)
        return render(request,'package.html',{'form': form})


def registerView(request):
    if request.method=="POST":
        form=SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
            form=SignUpForm()
    return render(request,'registration/register.html',{'form': form})

@login_required
def HotelView(request):
    city_choices = _city_options()
    if request.method=="POST":
        form = HotelForm(request.POST, city_choices=city_choices)
        filter_form = SearchFilterForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city'].strip() if form.cleaned_data['city'] else ''
            if not city:
                first_city = City.objects.order_by('city').values_list('city', flat=True).first()
                city = first_city or ''
            date = form.cleaned_data['date']
            hotels = Hotels.objects.filter(city__city__icontains=city) if city else Hotels.objects.none()
            # Apply filters
            if filter_form.is_valid():
                price_range = filter_form.cleaned_data.get('price_range')
                rating = filter_form.cleaned_data.get('rating')
                sort_by = filter_form.cleaned_data.get('sort_by')
                max_price = filter_form.cleaned_data.get('max_price')

                if price_range:
                    if price_range == '0-5000':
                        hotels = hotels.filter(hotel_price__lte=5000)
                    elif price_range == '5000-10000':
                        hotels = hotels.filter(hotel_price__gt=5000, hotel_price__lte=10000)
                    elif price_range == '10000-15000':
                        hotels = hotels.filter(hotel_price__gt=10000, hotel_price__lte=15000)
                    elif price_range == '15000-0':
                        hotels = hotels.filter(hotel_price__gt=15000)

                if rating:
                    if rating == '4-5':
                        hotels = hotels.filter(avg_rating__gte=4)
                    elif rating == '3-4':
                        hotels = hotels.filter(avg_rating__gte=3, avg_rating__lt=4)
                    elif rating == '2-3':
                        hotels = hotels.filter(avg_rating__gte=2, avg_rating__lt=3)

                if sort_by:
                    if sort_by == 'price_low':
                        hotels = hotels.order_by('hotel_price')
                    elif sort_by == 'price_high':
                        hotels = hotels.order_by('-hotel_price')
                    elif sort_by == 'rating':
                        hotels = hotels.order_by('-avg_rating')

                if max_price is not None:
                    hotels = hotels.filter(hotel_price__lte=max_price)
            
            # Get airport information
            city_airport = get_airport_info(city)
            
            d = {'date':date}
            h = {'Hotels':hotels}
            form_dict = {'form': form}
            city_ap = {'city_airport': city_airport}
            response = {**h,**d,**form_dict,**city_ap}
            response['filter_form'] = filter_form
            return render(request,'hotels.html',response)
        else:
            return render(request,'hotels.html',{'form': form, 'filter_form': SearchFilterForm()})
    else:
        form = HotelForm(city_choices=city_choices)
        return render(request,'hotels.html',{'form': form, 'filter_form': SearchFilterForm()})

@login_required
def FlightView(request):
    source_choices, destination_choices = _flight_route_options()
    c = 0;
    if request.method=="POST":
        form = FlightForm(request.POST, source_choices=source_choices, destination_choices=destination_choices)
        filter_form = SearchFilterForm(request.POST)
        if form.is_valid():
            source = form.cleaned_data['source'].strip() if form.cleaned_data['source'] else ''
            destination = form.cleaned_data['destination'].strip() if form.cleaned_data['destination'] else ''
            date = form.cleaned_data['date']
            
            # Search with case-insensitive and flexible matching
            flights = Flights.objects.filter(
                source__icontains=source
            ).filter(
                destination__icontains=destination
            ) if source and destination else Flights.objects.none()

            # Apply search filters if provided
            if filter_form.is_valid():
                price_range = filter_form.cleaned_data.get('price_range')
                rating = filter_form.cleaned_data.get('rating')
                sort_by = filter_form.cleaned_data.get('sort_by')
                max_price = filter_form.cleaned_data.get('max_price')
                airline = (filter_form.cleaned_data.get('airline') or '').strip()

                if price_range:
                    if price_range == '0-5000':
                        flights = flights.filter(eprice__lte=5000)
                    elif price_range == '5000-10000':
                        flights = flights.filter(eprice__gt=5000, eprice__lte=10000)
                    elif price_range == '10000-15000':
                        flights = flights.filter(eprice__gt=10000, eprice__lte=15000)
                    elif price_range == '15000-0':
                        flights = flights.filter(eprice__gt=15000)

                if rating:
                    if rating == '4-5':
                        flights = flights.filter(avg_rating__gte=4)
                    elif rating == '3-4':
                        flights = flights.filter(avg_rating__gte=3, avg_rating__lt=4)
                    elif rating == '2-3':
                        flights = flights.filter(avg_rating__gte=2, avg_rating__lt=3)

                if sort_by:
                    if sort_by == 'price_low':
                        flights = flights.order_by('eprice')
                    elif sort_by == 'price_high':
                        flights = flights.order_by('-eprice')
                    elif sort_by == 'rating':
                        flights = flights.order_by('-avg_rating')
                    elif sort_by == 'dept_early':
                        flights = flights.order_by('dept_time')
                    elif sort_by == 'dept_late':
                        flights = flights.order_by('-dept_time')

                if max_price is not None:
                    flights = flights.filter(eprice__lte=max_price)

                if airline:
                    flights = flights.filter(company__icontains=airline)
            
            # Get airport information
            source_airport = get_airport_info(source)
            dest_airport = get_airport_info(destination)

            # Build flight -> connection suggestions mapping based on stations
            flight_pairs = []
            for fl in flights:
                stations = fl.stations_list if hasattr(fl, 'stations_list') else []
                route_segments = []
                if len(stations) > 1:
                    for idx in range(len(stations) - 1):
                        route_segments.append({
                            'from': stations[idx],
                            'to': stations[idx + 1],
                            'segment_no': idx + 1,
                        })
                # Find other flights that start at any station/waypoint of this flight
                connections = Flights.objects.none()
                if stations:
                    connections = Flights.objects.filter(source__in=stations).exclude(id=fl.id)
                station_connections = []
                for st in stations:
                    st_connections = Flights.objects.filter(source__iexact=st).exclude(id=fl.id).order_by('dept_time')[:5]
                    if st_connections:
                        station_connections.append({'station': st, 'flights': st_connections})
                flight_pairs.append({
                    'flight': fl,
                    'connections': connections,
                    'route_segments': route_segments,
                    'station_connections': station_connections,
                })

            # If no direct flights, suggest nearby destination flights and one-stop routes.
            nearby_destination_flights = Flights.objects.none()
            one_stop_routes = []

            if source:
                nearby_destination_flights = Flights.objects.filter(source__icontains=source)
                if destination:
                    nearby_destination_flights = nearby_destination_flights.exclude(destination__icontains=destination)
                nearby_destination_flights = nearby_destination_flights.order_by('eprice')[:10]

                if destination:
                    first_legs = Flights.objects.filter(source__icontains=source).order_by('eprice')[:15]
                    for leg1 in first_legs:
                        leg2 = Flights.objects.filter(
                            source__icontains=leg1.destination,
                            destination__icontains=destination,
                        ).exclude(id=leg1.id).order_by('eprice').first()
                        if leg2:
                            one_stop_routes.append({'leg1': leg1, 'leg2': leg2})
                        if len(one_stop_routes) >= 8:
                            break

            d = {'date':date}
            form_dict = {'form': form}
            no_results = not flights.exists()
            nr = {'no_results': no_results}
            source_ap = {'source_airport': source_airport}
            dest_ap = {'dest_airport': dest_airport}
            response = {
                **d,
                **form_dict,
                **nr,
                **source_ap,
                **dest_ap,
                'FlightPairs': flight_pairs,
                'nearby_destination_flights': nearby_destination_flights,
                'one_stop_routes': one_stop_routes,
                'source_query': source,
                'destination_query': destination,
            }
            response['filter_form'] = filter_form
            return render(request,'flights.html',response)
        else:
            return render(request,'flights.html',{'form': form, 'filter_form': SearchFilterForm()})
    else:
        form = FlightForm(source_choices=source_choices, destination_choices=destination_choices)
        filter_form = SearchFilterForm()
        return render(request,'flights.html',{'form': form, 'filter_form': filter_form})

@login_required
def Dashboard(request):
    user = request.user
    f1 = BookFlight.objects.filter(username_id=user).order_by('-booking_date')
    h1 = BookHotel.objects.filter(username_id=user).order_by('-booking_date')
    p1 = BookPackage.objects.filter(username_id=user).order_by('-booking_date')
    
    # Advanced Analytics
    total_spent = sum([b.total_price for b in f1]) + sum([b.total_price for b in h1]) + sum([b.total_price for b in p1])
    total_bookings = f1.count() + h1.count() + p1.count()
    try:
        profile = UserProfile.objects.get(user=user)
        loyalty_points = profile.loyalty_points
    except UserProfile.DoesNotExist:
        loyalty_points = 0

    response= {
        'flights':f1,
        'hotels':h1,
        'packages':p1,
        'total_spent': total_spent,
        'total_bookings': total_bookings,
        'loyalty_points': loyalty_points
    }
    return render(request,'dashboard.html',response)

@login_required
def Flightbook(request,flight_num=None,date=None):
    cs=0
    c = None
    price = 0;
    if request.method=="POST":
        form = SeatForm(request.POST)
        if form.is_valid():
            seats = form.cleaned_data['seats']
            route_segments = []
            station_connections = []
            seatrem, flight_obj = _remaining_flight_seats(flight_num, date)
            if not flight_obj:
                return render(request, 'bookflight.html', {
                    'form': form,
                    'error_message': 'Flight not found.'
                })

            price = seats * flight_obj.eprice
            c = BookFlight.objects.filter(flight=flight_obj.flight_num).filter(date=date, status='confirmed')
            d = BookPackage.objects.filter(flight=flight_obj.flight_num).filter(date=date, status='confirmed')
            stations = flight_obj.stations_list if hasattr(flight_obj, 'stations_list') else []
            if len(stations) > 1:
                for idx in range(len(stations) - 1):
                    route_segments.append({
                        'from': stations[idx],
                        'to': stations[idx + 1],
                        'segment_no': idx + 1,
                    })
            for st in stations:
                st_connections = Flights.objects.filter(source__iexact=st).exclude(id=flight_obj.id).order_by('dept_time')[:5]
                if st_connections:
                    station_connections.append({'station': st, 'flights': st_connections})

            avail = "available" if seatrem >= seats else "unavailable"
            a = {'availability':avail}
            p = {'price':price}
            sb = {'seatsreq':seats}
            s = {'seatrem':seatrem}
            b = {'flight': Flights.objects.filter(id=flight_obj.id)}
            f = {'form':form}
            d_dict = {'date':date}
            response = {**b,**d_dict,**f,**s,**a,**sb,**p}
            response['route_segments'] = route_segments
            response['station_connections'] = station_connections
            print(s)
            return render(request,'bookflight.html',response)
        else:
            return render(request,'bookflight.html',{'form':form})
    else:
        form = SeatForm()
        return render(request,'bookflight.html',{'form':form})

@login_required
def FlightSubmit(request,flight_num=None,date=None,seat=None):
    user = request.user
    seat = int(seat)
    remaining, flight_obj = _remaining_flight_seats(flight_num, date)
    if not flight_obj or remaining is None or seat <= 0 or seat > remaining:
        return redirect('bookflight', flight_num=flight_num, date=date)
    b = BookFlight(username_id=user,flight=flight_num,date=date,seat=seat,total_price=seat * flight_obj.eprice)
    b.save()
    return redirect('dashboard')

@login_required
def Hotelbook(request, hotel=None, date=None):
    """
    Hotel booking view that shows booking details form for a specific hotel
    """
    # Resolve hotel parameter robustly (id, encoded name, slug, partial)
    from urllib.parse import unquote_plus
    hotel_param = hotel
    if hotel_param:
        hotel_param = unquote_plus(str(hotel_param)).strip()

    hotel_obj = None
    # try id
    if hotel_param and hotel_param.isdigit():
        hotel_obj = Hotels.objects.filter(id=int(hotel_param)).first()
    # try exact case-insensitive
    if not hotel_obj and hotel_param:
        hotel_obj = Hotels.objects.filter(hotel_name__iexact=hotel_param).first()
    # try hyphen replaced
    if not hotel_obj and hotel_param and '-' in hotel_param:
        hotel_obj = Hotels.objects.filter(hotel_name__iexact=hotel_param.replace('-', ' ')).first()
    # try partial
    if not hotel_obj and hotel_param:
        hotel_obj = Hotels.objects.filter(hotel_name__icontains=hotel_param).first()

    if not hotel_obj:
        return render(request, 'bookhotel.html', {
            'error_message': 'Hotel not found.'
        })
    
    # Check room availability
    roomrem, _ = _remaining_hotel_rooms(hotel, date)
    
    if request.method == "POST":
        form = HotelBookingDetailsForm(request.POST)
        if form.is_valid():
            room_type = form.cleaned_data.get('room_type', 'double')
            checkout_date = form.cleaned_data.get('checkout_date')
            guest_count = form.cleaned_data.get('guest_count', 2)
            has_breakfast = form.cleaned_data.get('has_breakfast', False)
            special_requests = form.cleaned_data.get('special_requests', '')
            
            # Calculate breakfast cost (example: 500 per room per night)
            breakfast_cost = 500 if has_breakfast else 0
            
            # Prepare response with single hotel details
            context = {
                'hotel': hotel_obj,
                'date': date,
                'checkout_date': checkout_date,
                'room_type': room_type,
                'guest_count': guest_count,
                'has_breakfast': has_breakfast,
                'breakfast_cost': breakfast_cost,
                'special_requests': special_requests,
                'roomrem': roomrem,
                'form': form,
                'availability': 'available' if roomrem > 0 else 'unavailable',
                'room_type_display': dict(form.fields['room_type'].choices).get(room_type, room_type)
            }
            return render(request, 'bookhotel.html', context)
        else:
            context = {
                'hotel': hotel_obj,
                'date': date,
                'form': form,
                'roomrem': roomrem,
                'availability': 'available' if roomrem > 0 else 'unavailable',
                'error_message': 'Please fill in all required fields correctly.'
            }
            return render(request, 'bookhotel.html', context)
    else:
        form = HotelBookingDetailsForm()
        context = {
            'hotel': hotel_obj,
            'date': date,
            'roomrem': roomrem,
            'availability': 'available' if roomrem > 0 else 'unavailable',
            'form': form,
            'show_details_form': True
        }
        return render(request, 'bookhotel.html', context)

@login_required
def HotelSubmit(request, hotel=None, date=None, room=None):
    user = request.user
    room = int(room)
    remaining, hotel_obj = _remaining_hotel_rooms(hotel, date)
    
    if not hotel_obj or remaining is None or room <= 0 or room > remaining:
        return redirect('bookhotel', hotel=hotel, date=date)
    
    # Get optional parameters from GET request
    checkout_date = request.GET.get('checkout_date', date)
    room_type = request.GET.get('room_type', 'double')
    guest_count = request.GET.get('guest_count', 2)
    has_breakfast = request.GET.get('has_breakfast', 'false').lower() == 'true'
    special_requests = request.GET.get('special_requests', '')
    
    # Calculate costs
    base_price = room * hotel_obj.hotel_price
    breakfast_cost = (500 * room) if has_breakfast else 0
    total_price = base_price + breakfast_cost
    
    # Create booking
    b = BookHotel(
        username_id=user,
        hotel_name=hotel,
        date=date,
        checkout_date=checkout_date,
        room=room,
        room_type=room_type,
        guest_count=int(guest_count),
        has_breakfast=has_breakfast,
        breakfast_cost=breakfast_cost,
        special_requests=special_requests,
        total_price=total_price
    )
    b.save()
    
    # Create notification
    Notification.objects.create(
        user=user,
        title=f'Hotel Booking Confirmed',
        message=f'Your booking at {hotel} for {date} has been confirmed.',
        notification_type='booking'
    )
    
    return redirect('dashboard')

@login_required
def PackageBook(request,source,city,date):
    c1={}
    d1={}
    roomrem=0
    price1=0
    cs = 0;
    cs1 = 0;
    allf = Flights.objects.filter(source=source).filter(destination=city)
    allh = Hotels.objects.filter(city__city__contains=city)
    af = {'allflights':allf}
    ah={'allhotels':allh}
    if request.method=="POST":
        form = ChoiceForm(request.POST)
        form1 = {'form': form}
        if form.is_valid():
            flight = form.cleaned_data['flight'].upper()
            hotel = form.cleaned_data['hotel']
            seats = form.cleaned_data['seats']
            room = form.cleaned_data['rooms']
            seatrem, flight_obj = _remaining_flight_seats(flight, date)
            roomrem, hotel_obj = _remaining_hotel_rooms(hotel, date)

            if flight_obj:
                price = seats * flight_obj.eprice
                flights = Flights.objects.filter(id=flight_obj.id)
                c = BookFlight.objects.filter(flight=flight_obj.flight_num).filter(date=date, status='confirmed')
                d = BookPackage.objects.filter(flight=flight_obj.flight_num).filter(date=date, status='confirmed')
                availf = "available" if seatrem >= seats else "unavailable"
            else:
                price = 0
                flights = Flights.objects.none()
                availf = "unavailable"

            if hotel_obj:
                price1 = room * hotel_obj.hotel_price
                hotels = Hotels.objects.filter(id=hotel_obj.id)
                c1 = BookHotel.objects.filter(hotel_name=hotel_obj.hotel_name).filter(date=date, status='confirmed')
                d1 = BookPackage.objects.filter(hotel_name=hotel_obj.hotel_name).filter(date=date, status='confirmed')
                availh = "available" if roomrem >= room else "unavailable"
            else:
                price1 = 0
                hotels = Hotels.objects.none()
                availh = "unavailable"

            a = {'flavailability':availf}
            p = {'pricef':price}
            sb = {'seatsreq':seats}
            s = {'seatrem':seatrem}
            a1 = {'havailability':availh}
            p1 = {'priceh':price1}
            rb = {'roomreq':room}
            r = {'roomrem':roomrem}
            f = {'Flights':flights}
            h = {'Hotels':hotels}
            d_dict = {'date':date}
            response = {**f,**af,**ah,**h,**d_dict,**form1,**a,**a1,**p,**p1,**s,**sb,**r,**rb}
            return render(request,'bookpackage.html',response)
        else:
            response = {**af,**ah,**form1}
            return render(request,'bookpackage.html',response)
    else:
        form = ChoiceForm()
        form1 = {'form': form}
        response = {**af,**ah,**form1}
        return render(request,'bookpackage.html',response)

@login_required
def PackageSubmit(request,flight=None,hotel=None,date=None,seat=None,room=None):
    user = request.user
    seat = int(seat)
    room = int(room)
    seatrem, flight_obj = _remaining_flight_seats(flight, date)
    roomrem, hotel_obj = _remaining_hotel_rooms(hotel, date)
    if not flight_obj or not hotel_obj or seatrem is None or roomrem is None or seat <= 0 or room <= 0 or seat > seatrem or room > roomrem:
        return redirect('package')
    total_price = (seat * flight_obj.eprice) + (room * hotel_obj.hotel_price)
    b = BookPackage(username_id=user,flight=flight,seat=seat,hotel_name=hotel,room=room,date=date,total_price=total_price)
    b.save()
    return redirect('dashboard')

@login_required
def CancelFlight(request,flight=None,date=None,seat=None):
    price = 0;
    flight = Flights.objects.filter(flight_num=flight)
    for i in flight:
        price = seat*i.eprice
    f = {'Flight':flight}
    p = {'price':price}
    s = {'seat':seat}
    d = {'date':date}
    response = {**f,**p,**s,**d}
    return render(request,'cancelflight.html',response)

@login_required
def ConfirmCancelFlight(request,flight=None,date=None,seat=None):
    user = request.user
    flight = BookFlight.objects.filter(username_id=user).filter(flight=flight).filter(date=date).filter(seat=seat)
    flight.delete()
    return redirect('dashboard')

@login_required
def CancelHotel(request,hotel=None,date=None,room=None):
    hotel = Hotels.objects.filter(hotel_name__iexact=hotel)
    for i in hotel:
        price = room*i.hotel_price
    h = {'Hotel':hotel}
    p = {'price':price}
    r = {'room':room}
    d = {'date':date}
    response = {**h,**p,**r,**d}
    return render(request,'cancelhotel.html',response)

@login_required
def ConfirmCancelHotel(request,hotel=None,date=None,room=None):
    user = request.user
    hotel = BookHotel.objects.filter(username_id=user).filter(hotel_name=hotel).filter(date=date).filter(room=room)
    hotel.delete()
    return redirect('dashboard')

@login_required
def CancelPackage(request,flight=None,seat=None,hotel=None,date=None,room=None):
    flight = Flights.objects.filter(flight_num=flight)
    hotel = Hotels.objects.filter(hotel_name__iexact=hotel)
    for i in hotel:
        price = room*i.hotel_price
    for j in flight:
        price1 = seat*j.eprice
    f = {'Flight':flight}
    p = {'pricef':price1}
    s = {'seat':seat}
    h = {'Hotel':hotel}
    p1 = {'priceh':price}
    r = {'room':room}
    d = {'date':date}
    response = {**h,**p,**r,**d,**f,**p1,**s}
    return render(request,'cancelpackage.html',response)

@login_required
def ConfirmCancelPackage(request,flight=None,seat=None,hotel=None,date=None,room=None):
    user = request.user
    package = BookPackage.objects.filter(username_id=user).filter(hotel_name=hotel).filter(date=date).filter(room=room).filter(flight=flight).filter(seat=seat)
    package.delete()
    return redirect('dashboard')

@login_required
def PlacesView(request):
    city_choices = _city_options()
    if request.method=="POST":
        form = CityForm(request.POST, city_choices=city_choices)
        if form.is_valid():
            city = form.cleaned_data['city']
            famplace = Famous.objects.filter(city__city__icontains=city)
            f = {'form':form}
            p = {'Famplace':famplace}
            response = {**f,**p}
            return render(request,'places.html',response)
        else:
            return render(request,'places.html',{'form':form})
    else:
        form = CityForm(city_choices=city_choices)
        return render(request,'places.html',{'form':form})


# ==================== NEW FEATURE VIEWS ====================

@login_required
@login_required
def UserProfileView(request):
    """User profile management"""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'profile/profile.html', context)


@login_required
def FlightReviewView(request, flight_id):
    """Add/View flight reviews"""
    flight = get_object_or_404(Flights, id=flight_id)
    user = request.user
    
    try:
        review = FlightReview.objects.get(user=user, flight=flight)
    except FlightReview.DoesNotExist:
        review = None
    
    if request.method == 'POST':
        form = FlightReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = user
            review.flight = flight
            review.save()
            
            # Update flight average rating
            avg_rating = FlightReview.objects.filter(flight=flight).aggregate(Avg('rating'))['rating__avg']
            flight.avg_rating = avg_rating or 0
            flight.save()
            
            # Create notification
            Notification.objects.create(
                user=user,
                notification_type='review_request',
                title='Review Submitted',
                message=f'Your review for flight {flight.flight_num} has been posted.'
            )
            
            return redirect('flight-reviews', flight_id=flight_id)
    else:
        form = FlightReviewForm(instance=review)
    
    all_reviews = FlightReview.objects.filter(flight=flight).order_by('-created_at')
    
    context = {
        'flight': flight,
        'form': form,
        'review': review,
        'all_reviews': all_reviews,
    }
    return render(request, 'reviews/flight_review.html', context)


@login_required
def HotelReviewView(request, hotel_id):
    """Add/View hotel reviews"""
    hotel = get_object_or_404(Hotels, id=hotel_id)
    user = request.user
    
    try:
        review = HotelReview.objects.get(user=user, hotel=hotel)
    except HotelReview.DoesNotExist:
        review = None
    
    if request.method == 'POST':
        form = HotelReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = user
            review.hotel = hotel
            review.save()
            
            # Update hotel average rating
            avg_rating = HotelReview.objects.filter(hotel=hotel).aggregate(Avg('rating'))['rating__avg']
            hotel.avg_rating = avg_rating or 0
            hotel.save()
            
            # Create notification
            Notification.objects.create(
                user=user,
                notification_type='review_request',
                title='Review Submitted',
                message=f'Your review for hotel {hotel.hotel_name} has been posted.'
            )
            
            return redirect('hotel-reviews', hotel_id=hotel_id)
    else:
        form = HotelReviewForm(instance=review)
    
    all_reviews = HotelReview.objects.filter(hotel=hotel).order_by('-created_at')
    
    context = {
        'hotel': hotel,
        'form': form,
        'review': review,
        'all_reviews': all_reviews,
    }
    return render(request, 'reviews/hotel_review.html', context)


@login_required
@login_required
@require_POST
def AddToWishlist(request, item_type, item_id):
    """Add flight or hotel to wishlist"""
    user = request.user
    
    if item_type == 'flight':
        flight = get_object_or_404(Flights, id=item_id)
        wishlist, created = Wishlist.objects.get_or_create(
            user=user,
            item_type='flight',
            flight=flight
        )
        message = 'Added to wishlist' if created else 'Already in wishlist'
    
    elif item_type == 'hotel':
        hotel = get_object_or_404(Hotels, id=item_id)
        wishlist, created = Wishlist.objects.get_or_create(
            user=user,
            item_type='hotel',
            hotel=hotel
        )
        message = 'Added to wishlist' if created else 'Already in wishlist'
    
    else:
        return JsonResponse({'error': 'Invalid item type'}, status=400)
    
    return JsonResponse({'success': True, 'message': message})


@login_required
def WishlistView(request):
    """View user's wishlist"""
    user = request.user
    wishlists = Wishlist.objects.filter(user=user).select_related('flight', 'hotel')
    
    flights = [w.flight for w in wishlists if w.flight]
    hotels = [w.hotel for w in wishlists if w.hotel]
    
    context = {
        'wishlists': wishlists,
        'flights': flights,
        'hotels': hotels,
        'total_items': wishlists.count(),
    }
    return render(request, 'wishlist/wishlist.html', context)


@login_required
def RemoveFromWishlist(request, wishlist_id):
    """Remove item from wishlist"""
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    wishlist.delete()
    return redirect('wishlist')


@login_required
def ApplyDiscountCode(request):
    """Apply discount code to booking"""
    if request.method == 'POST':
        form = DiscountCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code'].upper()
            try:
                discount = Discount.objects.get(code=code)
                if discount.can_use():
                    return JsonResponse({
                        'success': True,
                        'discount_id': discount.id,
                        'discount_type': discount.discount_type,
                        'discount_value': discount.discount_value,
                        'description': discount.description,
                    })
                else:
                    return JsonResponse({'success': False, 'message': 'Discount code expired or no usage left'})
            except Discount.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Invalid discount code'})
    
    form = DiscountCodeForm()
    return render(request, 'discount/apply_discount.html', {'form': form})


@login_required
def GenerateInvoice(request, booking_type, booking_id):
    """Generate booking invoice"""
    user = request.user
    
    if booking_type == 'flight':
        booking = get_object_or_404(BookFlight, id=booking_id, username_id=user)
        flight = Flights.objects.filter(flight_num=booking.flight).first()
        subtotal = booking.total_price or (booking.seat * flight.eprice if flight else 0)
        
    elif booking_type == 'hotel':
        booking = get_object_or_404(BookHotel, id=booking_id, username_id=user)
        hotel = Hotels.objects.filter(hotel_name=booking.hotel_name).first()
        subtotal = booking.total_price or (booking.room * hotel.hotel_price if hotel else 0)
        
    elif booking_type == 'package':
        booking = get_object_or_404(BookPackage, id=booking_id, username_id=user)
        flight = Flights.objects.filter(flight_num=booking.flight).first()
        hotel = Hotels.objects.filter(hotel_name=booking.hotel_name).first()
        subtotal = booking.total_price or ((booking.seat * flight.eprice if flight else 0) + (booking.room * hotel.hotel_price if hotel else 0))
    
    else:
        return redirect('dashboard')
    
    # Apply discount if provided
    discount = None
    discount_amount = 0
    if request.method == 'POST':
        discount_id = request.POST.get('discount_id')
        if discount_id:
            discount = get_object_or_404(Discount, id=discount_id)
            if discount.discount_type == 'percentage':
                discount_amount = int(subtotal * discount.discount_value / 100)
            else:
                discount_amount = discount.discount_value
    
    tax = int(subtotal * 0.05)  # 5% tax
    total_amount = subtotal - discount_amount + tax
    
    # Create invoice
    invoice_number = f"INV-{user.id}-{booking_id}-{timezone.now().timestamp()}"
    invoice = Invoice.objects.create(
        invoice_number=invoice_number,
        user=user,
        booking_type=booking_type,
        subtotal=subtotal,
        discount_amount=discount_amount,
        tax=tax,
        total_amount=total_amount,
        discount_code=discount,
        due_date=timezone.now().date(),
    )
    
    if booking_type == 'flight':
        invoice.booking_flight = booking
    elif booking_type == 'hotel':
        invoice.booking_hotel = booking
    elif booking_type == 'package':
        invoice.booking_package = booking
    
    invoice.save()
    
    # Update discount usage
    if discount:
        discount.usage_count += 1
        discount.save()
    
    context = {
        'invoice': invoice,
        'booking': booking,
        'booking_type': booking_type,
        'booking_id': booking_id,
    }

    # Send invoice email to user if email is configured
    try:
        subject = f"Your Invoice {invoice.invoice_number} from TripMate"
        message = f"Hello {user.username},\n\nYour invoice {invoice.invoice_number} for {booking_type} booking is generated. Total amount: ₹{invoice.total_amount}.\n\nThank you for using TripMate.\n"
        recipient = [user.email]
        if settings.EMAIL_HOST and user.email:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient, fail_silently=True)
    except Exception:
        pass
    return render(request, 'invoice/invoice.html', context)


@login_required
def PaymentView(request, invoice_id):
    """Process payment"""
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    if invoice.booking_type == 'flight' and invoice.booking_flight:
        booking_id = invoice.booking_flight.id
    elif invoice.booking_type == 'hotel' and invoice.booking_hotel:
        booking_id = invoice.booking_hotel.id
    elif invoice.booking_type == 'package' and invoice.booking_package:
        booking_id = invoice.booking_package.id
    else:
        booking_id = None
    
    # Check if payment already exists
    try:
        payment = Payment.objects.get(invoice=invoice)
    except Payment.DoesNotExist:
        payment = None
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.user = request.user
            payment.amount = invoice.total_amount
            payment.transaction_id = f"TXN-{invoice.id}-{timezone.now().timestamp()}"
            payment.status = 'completed'
            payment.payment_date = timezone.now()
            payment.save()
            
            # Update invoice payment status
            invoice.payment_status = 'completed'
            invoice.save()
            
            # Create notification
            Notification.objects.create(
                user=request.user,
                notification_type='booking_confirmed',
                title='Payment Successful',
                message=f'Payment of ₹{invoice.total_amount} has been received.',
            )
            # Send payment confirmation email
            try:
                subject = f"Payment Received - {invoice.invoice_number}"
                message = f"Hello {request.user.username},\n\nWe have received your payment of ₹{invoice.total_amount} for invoice {invoice.invoice_number}. Thank you for booking with TripMate.\n\nRegards,\nTripMate Team"
                recipient = [request.user.email]
                if settings.EMAIL_HOST and request.user.email:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient, fail_silently=True)
            except Exception:
                pass
            
            return redirect('payment-success', invoice_id=invoice_id)
    else:
        form = PaymentForm()
    
    context = {
        'invoice': invoice,
        'form': form,
        'payment': payment,
        'booking_id': booking_id,
    }
    return render(request, 'payment/payment.html', context)


@login_required
def PaymentSuccessView(request, invoice_id):
    """Payment success page"""
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    payment = get_object_or_404(Payment, invoice=invoice)
    if invoice.booking_type == 'flight' and invoice.booking_flight:
        booking_id = invoice.booking_flight.id
    elif invoice.booking_type == 'hotel' and invoice.booking_hotel:
        booking_id = invoice.booking_hotel.id
    elif invoice.booking_type == 'package' and invoice.booking_package:
        booking_id = invoice.booking_package.id
    else:
        booking_id = None
    
    context = {
        'invoice': invoice,
        'payment': payment,
        'booking_id': booking_id,
    }
    return render(request, 'payment/payment_success.html', context)


@login_required
def NotificationsView(request):
    """View all notifications"""
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/notifications.html', context)


@login_required
@require_POST
def MarkNotificationAsRead(request, notification_id):
    """Mark notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})


@login_required
@login_required
def SearchHistoryView(request):
    """View search history"""
    user = request.user
    search_history = SearchHistory.objects.filter(user=user).order_by('-search_date')[:50]
    
    context = {
        'search_history': search_history,
    }
    return render(request, 'history/search_history.html', context)


@login_required
def AutocompleteAPI(request):
    """Simple autocomplete API for flight sources/destinations and hotel cities.
    Query params: q (partial text), type (source|destination|city)
    """
    q = request.GET.get('q', '').strip()
    typ = request.GET.get('type', 'source')
    results = []
    if not q:
        return JsonResponse({'results': results})

    if typ == 'source':
        results = list(Flights.objects.filter(source__istartswith=q).values_list('source', flat=True).distinct()[:10])
    elif typ == 'destination':
        results = list(Flights.objects.filter(destination__istartswith=q).values_list('destination', flat=True).distinct()[:10])
    elif typ == 'city':
        results = list(City.objects.filter(city__istartswith=q).values_list('city', flat=True).distinct()[:10])
    else:
        results = []

    return JsonResponse({'results': results})


@login_required
def UnreadNotificationCountAPI(request):
    """Return unread notification count for navbar badge."""
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': unread_count})


@login_required
def BookingHistoryView(request):
    """View complete booking history with filters"""
    user = request.user
    
    flights = BookFlight.objects.filter(username_id=user).order_by('-booking_date')
    hotels = BookHotel.objects.filter(username_id=user).order_by('-booking_date')
    packages = BookPackage.objects.filter(username_id=user).order_by('-booking_date')
    
    # Booking status filter
    status_filter = request.GET.get('status')
    if status_filter:
        flights = flights.filter(status=status_filter)
        hotels = hotels.filter(status=status_filter)
        packages = packages.filter(status=status_filter)
    
    context = {
        'flights': flights,
        'hotels': hotels,
        'packages': packages,
        'total_bookings': flights.count() + hotels.count() + packages.count(),
    }
    return render(request, 'history/booking_history.html', context)


@staff_member_required
def AddHotelView(request):
    """Admin/staff view to add a hotel to the system"""
    if request.method == 'POST':
        form = HotelCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hotel added successfully.')
            return redirect('add_hotel')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = HotelCreateForm()

    context = {
        'form': form,
    }
    return render(request, 'add_hotel.html', context)

def LoyaltyPointsView(request):
    """View loyalty points"""
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    # Calculate points from bookings
    flights = BookFlight.objects.filter(username_id=user).count()
    hotels = BookHotel.objects.filter(username_id=user).count()
    packages = BookPackage.objects.filter(username_id=user).count()
    
    points = (flights + hotels + packages) * 10  # 10 points per booking
    profile.loyalty_points = points
    profile.save()

    # Progress widths are computed in Python to avoid unsupported template math filters.
    bronze_progress = 100 if points >= 0 else 0
    silver_progress = min(100, int((points / 250) * 100)) if points > 0 else 0
    gold_progress = min(100, int((points / 250) * 100)) if points > 0 else 0

    if points >= 250:
        tier = 'Gold'
    elif points >= 100:
        tier = 'Silver'
    else:
        tier = 'Bronze'
    
    context = {
        'profile': profile,
        'points': points,
        'bookings': flights + hotels + packages,
        'bronze_progress': bronze_progress,
        'silver_progress': silver_progress,
        'gold_progress': gold_progress,
        'tier': tier,
    }
    return render(request, 'loyalty/loyalty_points.html', context)

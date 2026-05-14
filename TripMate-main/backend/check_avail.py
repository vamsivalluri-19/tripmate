from django.test import RequestFactory
from django.contrib.auth.models import User
from travelapp.views import Hotelbook, Flightbook, PackageBook
from travelapp.models import Hotels, Flights

rf = RequestFactory()
user = User.objects.first()

# Hotel check
h = Hotels.objects.first()
date='2026-05-12'
if h:
    req = rf.post(f'/bookhotel/{h.hotel_name}/{date}', data={'rooms':'1'})
    req.user = user
    resp = Hotelbook(req, hotel=h.hotel_name, date=date)
    html = resp.content.decode('utf-8', errors='ignore')
    print('HOTEL:', h.hotel_name)
    print('AVAILABLE?', 'available' in html.lower(), 'UNAVAILABLE?', 'unavailable' in html.lower())
else:
    print('No hotels')

# Flight check
f = Flights.objects.first()
if f:
    req = rf.post(f'/bookflight/{f.flight_num}/{date}', data={'seats':'1'})
    req.user = user
    resp = Flightbook(req, flight_num=f.flight_num, date=date)
    html = resp.content.decode('utf-8', errors='ignore')
    print('FLIGHT:', f.flight_num)
    print('AVAILABLE?', 'available' in html.lower(), 'UNAVAILABLE?', 'unavailable' in html.lower())
else:
    print('No flights')

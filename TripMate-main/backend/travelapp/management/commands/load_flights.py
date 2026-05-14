from datetime import time

from django.core.management.base import BaseCommand
from django.db import transaction

from travelapp.models import City, Famous, Flights, Hotels


AIRLINES = [
    "TripMate Air",
    "TripMate Connect",
    "TripMate Regional",
    "SkyLink",
    "BlueWings",
]

CORE_CITIES = [
    "Delhi",
    "Mumbai",
    "Bengaluru",
    "Hyderabad",
    "Chennai",
    "Kolkata",
    "Goa",
    "Jaipur",
    "Kochi",
    "Pune",
    "Ahmedabad",
    "Lucknow",
]

LEGACY_CITIES = [
    "DELHI",
    "MUMBAI",
    "COCHIN",
    "DARJEELING",
    "SRINAGAR",
    "ZURICH",
    "LONDON",
    "NEW YORK",
    "International",
]

ALL_CITY_ORDER = CORE_CITIES + LEGACY_CITIES


def _city_links(city_name):
    slug = city_name.lower().replace(" ", "-")
    return {
        "bestlink": f"https://tripmate.example/{slug}/best",
        "weekgetlinks": f"https://tripmate.example/{slug}/week",
    }


def _build_flight_record(index, source, destination, stations, step):
    dep_hour = 5 + (index % 14)
    dep_min = (index * 7) % 60
    duration = 70 + (step * 35) + (index % 40)
    arr_total = dep_hour * 60 + dep_min + duration
    arr_hour = (arr_total // 60) % 24
    arr_min = arr_total % 60

    return {
        "flight_num": f"TMX{index:03d}",
        "source": source,
        "destination": destination,
        "company": AIRLINES[index % len(AIRLINES)],
        "eprice": 2200 + (index * 95) + (step * 420),
        "seats": 70 + (index % 80),
        "dept_time": time(dep_hour, dep_min),
        "dest_time": time(arr_hour, arr_min),
        "city": destination,
        "stations": ",".join(stations),
    }


class Command(BaseCommand):
    help = "Load a large connected demo dataset for all city routes, stations, hotels, and places"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing Flights/Hotels/Famous/City rows before loading",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options.get("reset"):
            self.stdout.write(self.style.WARNING("Reset enabled: deleting existing travel dataset..."))
            Famous.objects.all().delete()
            Hotels.objects.all().delete()
            Flights.objects.all().delete()
            City.objects.all().delete()

        city_map = {}
        for city_name in ALL_CITY_ORDER:
            obj, _ = City.objects.update_or_create(city=city_name, defaults=_city_links(city_name))
            city_map[city_name] = obj

        flights_payload = []
        n = len(ALL_CITY_ORDER)
        flight_index = 1

        # One-to-next connected routes for all cities in sequence.
        for i, src in enumerate(ALL_CITY_ORDER):
            dst = ALL_CITY_ORDER[(i + 1) % n]
            flights_payload.append(
                _build_flight_record(
                    flight_index,
                    src,
                    dst,
                    [src, dst],
                    step=1,
                )
            )
            flight_index += 1

        # Additional connector routes with mid stations to strengthen graph connectivity.
        for i, src in enumerate(ALL_CITY_ORDER):
            mid = ALL_CITY_ORDER[(i + 1) % n]
            dst = ALL_CITY_ORDER[(i + 2) % n]
            flights_payload.append(
                _build_flight_record(
                    flight_index,
                    src,
                    dst,
                    [src, mid, dst],
                    step=2,
                )
            )
            flight_index += 1

        # Long connectors every 4th city with two mid stations.
        for i, src in enumerate(ALL_CITY_ORDER):
            if i % 2 == 0:
                mid1 = ALL_CITY_ORDER[(i + 1) % n]
                mid2 = ALL_CITY_ORDER[(i + 2) % n]
                dst = ALL_CITY_ORDER[(i + 4) % n]
                flights_payload.append(
                    _build_flight_record(
                        flight_index,
                        src,
                        dst,
                        [src, mid1, mid2, dst],
                        step=4,
                    )
                )
                flight_index += 1

        created_flights = 0
        for payload in flights_payload:
            _, created = Flights.objects.update_or_create(
                flight_num=payload["flight_num"],
                defaults={
                    "source": payload["source"],
                    "destination": payload["destination"],
                    "company": payload["company"],
                    "eprice": payload["eprice"],
                    "seats": payload["seats"],
                    "dept_time": payload["dept_time"],
                    "dest_time": payload["dest_time"],
                    "city": city_map[payload["city"]],
                    "stations": payload["stations"],
                },
            )
            if created:
                created_flights += 1

        normalized_stations = 0
        for fl in Flights.objects.all():
            if not fl.stations:
                fl.stations = f"{fl.source},{fl.destination}"
                fl.save(update_fields=["stations"])
                normalized_stations += 1

        hotels_payload = []
        for city_name in ALL_CITY_ORDER:
            hotels_payload.append(
                {
                    "city": city_name,
                    "hotel_name": f"TripMate {city_name} Central Hotel",
                    "hotel_address": f"Main Road, {city_name}",
                    "hotel_price": 3200 + (len(city_name) * 70),
                    "hotel_rating": 4,
                    "amenities": "WiFi,Breakfast,Airport Transfer",
                    "distfromap": 10 + (len(city_name) % 19),
                    "rooms": 25 + (len(city_name) % 40),
                }
            )

        for city_name in CORE_CITIES:
            hotels_payload.append(
                {
                    "city": city_name,
                    "hotel_name": f"TripMate {city_name} Grand Suites",
                    "hotel_address": f"Business District, {city_name}",
                    "hotel_price": 5200 + (len(city_name) * 90),
                    "hotel_rating": 5,
                    "amenities": "WiFi,Pool,Spa,Gym,Breakfast",
                    "distfromap": 8 + (len(city_name) % 14),
                    "rooms": 40 + (len(city_name) % 50),
                }
            )

        created_hotels = 0
        for payload in hotels_payload:
            _, created = Hotels.objects.update_or_create(
                hotel_name=payload["hotel_name"],
                defaults={
                    "city": city_map[payload["city"]],
                    "hotel_address": payload["hotel_address"],
                    "hotel_price": payload["hotel_price"],
                    "hotel_rating": payload["hotel_rating"],
                    "amenities": payload["amenities"],
                    "distfromap": payload["distfromap"],
                    "rooms": payload["rooms"],
                },
            )
            if created:
                created_hotels += 1

        places_payload = []
        for city_name in ALL_CITY_ORDER:
            places_payload.append(
                {
                    "city": city_name,
                    "place_name": f"{city_name} Heritage Square",
                    "desc": f"Popular central landmark and cultural spot in {city_name}.",
                }
            )

        for city_name in CORE_CITIES:
            places_payload.append(
                {
                    "city": city_name,
                    "place_name": f"{city_name} Riverside Walk",
                    "desc": f"Well-known leisure and sightseeing promenade in {city_name}.",
                }
            )

        created_places = 0
        for payload in places_payload:
            _, created = Famous.objects.update_or_create(
                city=city_map[payload["city"]],
                place_name=payload["place_name"],
                defaults={"desc": payload["desc"]},
            )
            if created:
                created_places += 1

        sources = Flights.objects.values_list("source", flat=True).distinct().count()
        destinations = Flights.objects.values_list("destination", flat=True).distinct().count()

        self.stdout.write(self.style.SUCCESS("Dataset update complete."))
        self.stdout.write(self.style.SUCCESS(f"Cities seeded: {len(ALL_CITY_ORDER)}"))
        self.stdout.write(self.style.SUCCESS(f"Total cities in DB: {City.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Flights seeded/updated: {len(flights_payload)} (new: {created_flights})"))
        self.stdout.write(self.style.SUCCESS(f"Flights normalized with fallback stations: {normalized_stations}"))
        self.stdout.write(self.style.SUCCESS(f"Hotels seeded/updated: {len(hotels_payload)} (new: {created_hotels})"))
        self.stdout.write(self.style.SUCCESS(f"Places seeded/updated: {len(places_payload)} (new: {created_places})"))
        self.stdout.write(self.style.SUCCESS(f"Unique source cities in flights: {sources}"))
        self.stdout.write(self.style.SUCCESS(f"Unique destination cities in flights: {destinations}"))
        self.stdout.write(self.style.SUCCESS("One-to-next station routes and connector flights are now available for all seeded cities."))

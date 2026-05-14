from django.core.management.base import BaseCommand
from travelapp.models import City, Hotels


class Command(BaseCommand):
    help = 'Seed sample cities and hotels dataset'

    def handle(self, *args, **options):
        sample_cities = [
            {'city': 'Mumbai', 'bestlink': 'mumbai', 'weekgetlinks': 'mumbai-week'},
            {'city': 'Delhi', 'bestlink': 'delhi', 'weekgetlinks': 'delhi-week'},
            {'city': 'Bengaluru', 'bestlink': 'bengaluru', 'weekgetlinks': 'bengaluru-week'},
            {'city': 'Goa', 'bestlink': 'goa', 'weekgetlinks': 'goa-week'},
            {'city': 'Chennai', 'bestlink': 'chennai', 'weekgetlinks': 'chennai-week'},
        ]

        hotels_by_city = {
            'Mumbai': [
                {'hotel_name': 'The Grand Mumbai', 'hotel_address': 'Marine Drive, Mumbai', 'hotel_price': 8000, 'hotel_rating': 5, 'amenities': 'WiFi,Pool,Spa', 'distfromap': 25, 'rooms': 50},
                {'hotel_name': 'Sea View Residency', 'hotel_address': 'Juhu Beach, Mumbai', 'hotel_price': 5500, 'hotel_rating': 4, 'amenities': 'WiFi,Breakfast', 'distfromap': 30, 'rooms': 30},
            ],
            'Delhi': [
                {'hotel_name': 'Capital Inn', 'hotel_address': 'Connaught Place, Delhi', 'hotel_price': 6000, 'hotel_rating': 4, 'amenities': 'WiFi,Gym', 'distfromap': 20, 'rooms': 40},
            ],
            'Bengaluru': [
                {'hotel_name': 'Tech Park Hotel', 'hotel_address': 'Electronic City, Bengaluru', 'hotel_price': 4500, 'hotel_rating': 3, 'amenities': 'WiFi,Parking', 'distfromap': 40, 'rooms': 60},
            ],
            'Goa': [
                {'hotel_name': 'Beachside Resort Goa', 'hotel_address': 'Calangute, Goa', 'hotel_price': 7000, 'hotel_rating': 5, 'amenities': 'Beach,Pool,Bar', 'distfromap': 15, 'rooms': 80},
            ],
            'Chennai': [
                {'hotel_name': 'Bayview Chennai', 'hotel_address': 'Marina Beach, Chennai', 'hotel_price': 4800, 'hotel_rating': 4, 'amenities': 'WiFi,Breakfast', 'distfromap': 10, 'rooms': 35},
            ],
        }

        created_cities = 0
        created_hotels = 0

        for c in sample_cities:
            city_obj, created = City.objects.get_or_create(city=c['city'], defaults={'bestlink': c['bestlink'], 'weekgetlinks': c['weekgetlinks']})
            if created:
                created_cities += 1

        for city_name, hotels in hotels_by_city.items():
            city_obj = City.objects.filter(city__iexact=city_name).first()
            if not city_obj:
                self.stdout.write(self.style.WARNING(f"City '{city_name}' not found, skipping hotels"))
                continue
            for h in hotels:
                # avoid duplicates
                if Hotels.objects.filter(hotel_name__iexact=h['hotel_name']).exists():
                    continue
                Hotels.objects.create(
                    city=city_obj,
                    hotel_name=h['hotel_name'],
                    hotel_address=h['hotel_address'],
                    hotel_price=h['hotel_price'],
                    hotel_rating=h['hotel_rating'],
                    amenities=h['amenities'],
                    distfromap=h['distfromap'],
                    rooms=h['rooms'],
                )
                created_hotels += 1

        self.stdout.write(self.style.SUCCESS(f"Seed complete: {created_cities} cities, {created_hotels} hotels added."))

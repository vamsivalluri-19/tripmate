from django.core.management.base import BaseCommand
from travelapp.models import Flights

class Command(BaseCommand):
    help = 'List all available flight routes'

    def handle(self, *args, **options):
        flights = Flights.objects.all()
        
        if not flights.exists():
            self.stdout.write(self.style.WARNING('No flights in database'))
            return
        
        self.stdout.write(self.style.SUCCESS('\n📋 AVAILABLE FLIGHT ROUTES:\n'))
        self.stdout.write('Flight | Airline | From → To | Price | Seats\n')
        self.stdout.write('-' * 70)
        
        for flight in flights:
            self.stdout.write(
                f'{flight.flight_num:6} | {flight.company:15} | {flight.source:10} → {flight.destination:10} | ${flight.eprice:4} | {flight.seats:3}\n'
            )
        
        # Show unique routes
        self.stdout.write(self.style.SUCCESS('\n🗺️  UNIQUE ROUTES (Search with these):\n'))
        routes = flights.values('source', 'destination').distinct()
        
        for i, route in enumerate(routes, 1):
            self.stdout.write(f'{i}. {route["source"]} → {route["destination"]}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Total flights: {flights.count()}\n'))

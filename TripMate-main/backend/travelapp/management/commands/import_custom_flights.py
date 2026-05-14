import json
import os
import re
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction

from travelapp.models import City, Flights, Hotels


def _city_links(city_name):
    slug = city_name.lower().replace(" ", "-")
    return {
        "bestlink": f"https://tripmate.example/{slug}/best",
        "weekgetlinks": f"https://tripmate.example/{slug}/week",
    }


def _parse_time(value):
    if not value:
        return None
    text = str(value).strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%H:%M:%S", "%H:%M"):
        try:
            dt = datetime.strptime(text, fmt)
            return dt.time()
        except ValueError:
            continue
    return None


def _flatten(items):
    out = []
    if isinstance(items, list):
        for item in items:
            out.extend(_flatten(item))
    elif isinstance(items, dict):
        out.append(items)
    return out


def _extract_objects_from_text(raw_text):
    # Fallback parser for malformed content with repeated nested array starts.
    objects = []
    for chunk in re.findall(r"\{[^{}]*\}", raw_text, flags=re.S):
        try:
            objects.append(json.loads(chunk))
        except Exception:
            continue
    return objects


class Command(BaseCommand):
    help = "Import custom flights JSON (supports malformed text by extracting JSON objects)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default=os.path.join("backend", "data", "custom_flights_raw.txt"),
            help="Path to JSON or raw text containing flight objects",
        )
        parser.add_argument(
            "--upsert-hotels",
            action="store_true",
            help="Create/update hotel placeholders from nearbyHotel",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        file_path = options["file"]
        upsert_hotels = options.get("upsert_hotels", False)

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"Input file not found: {file_path}"))
            return

        with open(file_path, "r", encoding="utf-8") as f:
            raw = f.read()

        records = []
        try:
            parsed = json.loads(raw)
            records = _flatten(parsed)
        except Exception:
            records = _extract_objects_from_text(raw)

        if not records:
            self.stdout.write(self.style.ERROR("No flight objects could be parsed from the input file."))
            return

        imported = 0
        skipped = 0
        hotels_added = 0

        for r in records:
            flight_num = (r.get("flightNumber") or "").strip()
            source = (r.get("from") or "").strip()
            destination = (r.get("to") or "").strip()

            if not flight_num or not source or not destination:
                skipped += 1
                continue

            city_obj, _ = City.objects.get_or_create(city=destination, defaults=_city_links(destination))
            City.objects.get_or_create(city=source, defaults=_city_links(source))

            dept = _parse_time(r.get("departure"))
            dest = _parse_time(r.get("arrival"))

            defaults = {
                "source": source,
                "destination": destination,
                "company": (r.get("airline") or "TripMate Air")[:15],
                "eprice": int(r.get("price") or 0),
                "seats": int(r.get("availableSeats") or 0),
                "dept_time": dept or datetime.strptime("09:00", "%H:%M").time(),
                "dest_time": dest or datetime.strptime("11:00", "%H:%M").time(),
                "city": city_obj,
                "stations": f"{source},{destination}",
            }

            Flights.objects.update_or_create(flight_num=flight_num[:10], defaults=defaults)
            imported += 1

            if upsert_hotels:
                hotel_name = (r.get("nearbyHotel") or "").strip()
                if hotel_name:
                    _, created = Hotels.objects.get_or_create(
                        hotel_name=hotel_name[:200],
                        defaults={
                            "city": city_obj,
                            "hotel_address": f"Central {destination}",
                            "hotel_price": max(2500, int((r.get("price") or 5000) * 0.3)),
                            "hotel_rating": 4,
                            "amenities": "WiFi,Breakfast",
                            "distfromap": 12,
                            "rooms": 25,
                        },
                    )
                    if created:
                        hotels_added += 1

        self.stdout.write(self.style.SUCCESS(f"Flights imported/updated: {imported}"))
        self.stdout.write(self.style.SUCCESS(f"Records skipped: {skipped}"))
        if upsert_hotels:
            self.stdout.write(self.style.SUCCESS(f"Hotels added from nearbyHotel: {hotels_added}"))
        self.stdout.write(self.style.SUCCESS("Stations field normalized as source,destination for imported flights."))

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
import pandas as pd
from api.models import Calendar, Trip, Stop, StopTime


django.setup()

def run():
    trips = Trip.objects.all()
    calendar = Calendar.objects.all()
    stop = Stop.objects.all()
    stop_time = StopTime.objects.all()

    for trip in trips:
        departure_time = trip['departure_time']

    print(departure_time)
import os
import pandas as pd
from datetime import datetime
from django.db import transaction
from api.models import Agency, Stop, Route, Trip, StopTime, Shape, FeedInfo, Calendar

# Setting the environment variable DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# "Django environment configuration"
import django
django.setup()

# Path to the directory containing GTFS files
GTFS_DIR = 'api/scripts/GTFS-ZTM/'

@transaction.atomic
def load_agency():
    Agency.objects.all().delete()
    df = pd.read_csv(os.path.join(GTFS_DIR, 'agency.txt'))
    for index, row in df.iterrows():
        Agency.objects.create(
            agency_id=row['agency_id'],
            agency_name=row['agency_name'],
            agency_url=row['agency_url'],
            agency_timezone=row['agency_timezone'],
            agency_lang=row.get('agency_lang'),
            agency_phone=row.get('agency_phone')        
            )

@transaction.atomic
def load_stops():
    Stop.objects.all().delete()

    df = pd.read_csv(os.path.join(GTFS_DIR, 'stops.txt'))
    for index, row in df.iterrows():
        Stop.objects.create(
            stop_id=row['stop_id'],
            stop_name=row['stop_name'],
            stop_code=row.get('stop_desc'),
            stop_lat=row['stop_lat'],
            stop_lon=row['stop_lon'],
            zone_id=row.get('zone_id'),
        )

@transaction.atomic
def load_routes():
    Route.objects.all().delete()

    df = pd.read_csv(os.path.join(GTFS_DIR, 'routes.txt'))
    for index, row in df.iterrows():
        agency = Agency.objects.get(agency_id=row['agency_id'])
        Route.objects.create(
            route_id=row['route_id'],
            agency_id=agency,
            route_short_name=row['route_short_name'],
            route_long_name=row['route_long_name'],
            route_desc=row.get('route_desc'),
            route_type=row['route_type'],
            route_color=row.get('route_color'),
            route_text_color=row.get('route_text_color')
        )

@transaction.atomic
def load_trips():
    Trip.objects.all().delete()

    df = pd.read_csv(os.path.join(GTFS_DIR, 'trips.txt'))
    for index, row in df.iterrows():
        service = Calendar.objects.get(service_id =row['service_id'])
        route = Route.objects.get(route_id=row['route_id'])
        shape = Shape.objects.get(shape_id=row['shape_id'])
        Trip.objects.create(
            trip_id=row['trip_id'],
            route_id=route,
            service_id=service,
            trip_headsign=row.get('trip_headsign'),
            wheelchair_accessible=row.get('wheelchair_accessible'),
            direction_id=row.get('direction_id'),
            brigade=row.get('brigade'),
            shape_id=shape
        )

@transaction.atomic
def load_stop_times():
    StopTime.objects.all().delete()

    df = pd.read_csv(os.path.join(GTFS_DIR, 'stop_times.txt'))
    for index, row in df.iterrows():
        trip_id = Trip.objects.get(trip_id=row['trip_id'])
        stop_id = Stop.objects.get(stop_id=row['stop_id'])
        StopTime.objects.create(
            trip_id=trip_id,
            arrival_time=row['arrival_time'],
            departure_time=row['departure_time'],
            stop_id=stop_id,
            stop_sequence=row['stop_sequence'],
            stop_headsign=row.get('stop_headsign'),
            pickup_type=row.get('pickup_type'),
            drop_off_type=row.get('drop_off_type'),
        )

@transaction.atomic
def load_shapes():
    Shape.objects.all().delete()

    df = pd.read_csv(os.path.join(GTFS_DIR, 'shapes.txt'))
    for index, row in df.iterrows():
        Shape.objects.create(
            shape_id=row['shape_id'],
            shape_pt_lat=row['shape_pt_lat'],
            shape_pt_lon=row['shape_pt_lon'],
            shape_pt_sequence=row['shape_pt_sequence'],
        )

@transaction.atomic
def load_feed_info():
    FeedInfo.objects.all().delete()

    df = pd.read_csv(os.path.join(GTFS_DIR, 'feed_info.txt'))
    df['feed_start_date'] = df['feed_start_date'].astype(str)
    df['feed_end_date'] = df['feed_end_date'].astype(str)
    for index, row in df.iterrows():
        FeedInfo.objects.create(
            feed_publisher_name=row['feed_publisher_name'],
            feed_publisher_url=row['feed_publisher_url'],
            feed_lang=row['feed_lang'],
            feed_start_date=datetime.strptime(row['feed_start_date'], '%Y%m%d').strftime('%Y-%m-%d'),
            feed_end_date=datetime.strptime(row['feed_end_date'], '%Y%m%d').strftime('%Y-%m-%d'),
        )
@transaction.atomic
def load_calendar():
    Calendar.objects.all().delete()

    df = pd.read_csv(os.path.join(GTFS_DIR, 'calendar.txt'))
    for index, row in df.iterrows():
        Calendar.objects.create(
            service_id=row['service_id'],
            monday=bool(row['monday']),
            tuesday=bool(row['tuesday']),
            wednesday=bool(row['wednesday']),
            thursday=bool(row['thursday']),
            friday=bool(row['friday']),
            saturday=bool(row['saturday']),
            sunday=bool(row['sunday']),
            start_date=pd.to_datetime(row['start_date'], format='%Y%m%d').date(),
            end_date=pd.to_datetime(row['end_date'], format='%Y%m%d').date()
        )


# Import date
load_agency()
load_stops()
load_routes()
load_calendar()
load_feed_info()
load_shapes()
load_trips()
load_stop_times()

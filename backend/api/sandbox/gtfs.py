import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
import pandas as pd
import csv
import logging
import requests
import json
import requests
import zipfile
import io
from datetime import datetime
from django.db import transaction
from api.models import Agency, Stop, Route, Trip, StopTime, Shape, FeedInfo, Calendar, ShapeId


django.setup()

# URL to the GTFS files
GTFS_URL = "https://www.ztm.poznan.pl/pl/dla-deweloperow/getGTFSFile"

# Path to the directory containing GTFS files
GTFS_DIR = 'api/GTFS-ZTM/GTFS-ZTM-STATIC'

# Function to download and extract GTFS files
def download_and_extract_gtfs(url, extract_to):
    try:
        print(f"Attempting to download GTFS data from {url}")
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(extract_to)
        print("GTFS data downloaded and extracted successfully.")
    except requests.exceptions.RequestException as e:
        raise

def convert_time_format(time_str):
    """
    Converts time strings in 'HH:MM:SS' format where HH can be >= 24 to a valid time.
    """
    hours, minutes, seconds = map(int, time_str.split(':'))
    if hours >= 24:
        hours -= 24
    return f'{hours:02}:{minutes:02}:{seconds:02}'


# Clear the GTFS directory before downloading new files

# if os.path.exists(GTFS_DIR):
#     for file in os.listdir(GTFS_DIR):
#         file_path = os.path.join(GTFS_DIR, file)
#         if os.path.isfile(file_path):
#             os.unlink(file_path)
#         elif os.path.isdir(file_path):
#             shutil.rmtree(file_path)

# Download and extract GTFS files
download_and_extract_gtfs(GTFS_URL, GTFS_DIR)

@transaction.atomic
def load_agency():
    try:
        # Deleting all records from table
        Agency.objects.all().delete()
        
        # Checking GTFS-ZTM exist
        if not os.path.exists(GTFS_DIR):
            raise FileNotFoundError(f"Directory {GTFS_DIR} doesn't exist.")
            
        
        # Checking that file exist
        file_path = os.path.join(GTFS_DIR, 'agency.txt')
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} doesn't exist.")
            
        
        # Loading files from CSV
        with open(file_path, 'r', encoding='utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                Agency.objects.create(
                    agency_id=row.get('agency_id'),
                    agency_name=row['agency_name'],
                    agency_url=row['agency_url'],
                    agency_timezone=row['agency_timezone'],     
                    )
        
        print("Agency loaded successfully.")
    
    except Exception as e:
        print(f"There was an error: {e}")
        raise

@transaction.atomic
def load_stops():
    try:
        # Deleting all records from table
        Stop.objects.all().delete()
        
        # Checking GTFS-ZTM exist
        if not os.path.exists(GTFS_DIR):
            print(f"Directory {GTFS_DIR} doesn't exist.")
            raise
        
        # Checking that file exist
        file_path = os.path.join(GTFS_DIR, 'stops.txt')
        if not os.path.exists(file_path):
            print(f"File {file_path} doesn't exist.")
            raise
        
        # Loading files from CSV
        with open(file_path, 'r', encoding='utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                
                Stop.objects.create(
                    stop_id=row['stop_id'],
                    stop_name=row['stop_name'],
                    stop_code=row.get('stop_desc'),
                    stop_lat=row['stop_lat'],
                    stop_lon=row['stop_lon'],
                    zone_id=row.get('zone_id'),
                )
        
        print("Load stops loaded successfully.")

    except Exception as e:
        print(f"There was an error: {e}")
        raise

@transaction.atomic
def load_routes():
    try:
        # Deleting all records from table
        Route.objects.all().delete()
        
        # Checking GTFS-ZTM exist
        if not os.path.exists(GTFS_DIR):
            print(f"Directory {GTFS_DIR} doesn't exist.")
            raise
        
        # Checking that file exist
        file_path = os.path.join(GTFS_DIR, 'routes.txt')
        if not os.path.exists(file_path):
            print(f"File {file_path} doesn't exist.")
            raise
        
        # Loading files from CSV
        with open(file_path, 'r', encoding='utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                
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
        
        print("Load routes loaded successfully.")
        
    except Exception as e:
        print(f"There was an error: {e}")
        raise

@transaction.atomic
def load_trips():
    try:
        # Deleting all records from table
        Trip.objects.all().delete()
        
        # Checking GTFS-ZTM exist
        if not os.path.exists(GTFS_DIR):
            raise FileNotFoundError(f"Directory {GTFS_DIR} doesn't exist.")
        
        # Checking that file exist
        file_path = os.path.join(GTFS_DIR, 'trips.txt')
        if not os.path.exists(file_path):
            raise FileExistsError(f"File {file_path} doesn't exist.")
        
        # Loading files from CSV
        with open(file_path, 'r',encoding='utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                logging.info(f"Loading trip_id: {row.get('trip_id')}")                
                service = Calendar.objects.get(service_id=row['service_id'])
                route = Route.objects.get(route_id=row['route_id'])
                shape_id = ShapeId.objects.get(shape_id=row['shape_id'])
                shape = Shape.objects.filter(shape_id=shape_id).first()
                
                Trip.objects.create(
                    trip_id=row['trip_id'],
                    route_id=route,
                    service_id=service,
                    trip_headsign=row.get('trip_headsign'),
                    wheelchair_accessible=row.get('wheelchair_accessible'),
                    direction_id=row.get('direction_id'),
                    brigade=row.get('brigade'),
                    shape=shape
                )
        print("Trips loaded successfully.")
            
    except ShapeId.DoesNotExist:
        print(f"ShapeId with shape_id {row['shape_id']} does not exist")
        raise
    except Exception as e:
        print(f"Error processing trip_id {row['trip_id']}: {e}")
        raise
        
@transaction.atomic
def load_stop_times():
    try:
        # Deleting all records from the table
        StopTime.objects.all().delete()
        
        # Checking GTFS-ZTM existence
        if not os.path.exists(GTFS_DIR):
            raise FileNotFoundError(f"Directory {GTFS_DIR} doesn't exist.")
        
        # Checking that the file exists
        file_path = os.path.join(GTFS_DIR, 'stop_times.txt')
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} doesn't exist.")
        
        # Loading data from CSV
        with open(file_path, 'r',encoding='utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                
                trip = Trip.objects.get(trip_id=row['trip_id'])
                arrival_time = convert_time_format(row['arrival_time'])
                departure_time = convert_time_format(row['departure_time'])
                stop = Stop.objects.get(stop_id=row['stop_id'])

                StopTime.objects.create(
                    trip_id=trip,
                    arrival_time=arrival_time,
                    departure_time=departure_time,
                    stop_id=stop,
                    stop_sequence=row['stop_sequence'],
                    stop_headsign=row.get('stop_headsign'),
                    pickup_type=row.get('pickup_type'),
                    drop_off_type=row.get('drop_off_type'),
                )
        print("Stop times loaded successfully.")
            
    except Trip.DoesNotExist:
        print(f"Trip with trip_id {row['trip_id']} does not exist")
        raise
    except Stop.DoesNotExist:
        print(f"Stop with stop_id {row['stop_id']} does not exist")
        raise
    except Exception as e:
        print(f"Error processing stop time for trip_id {row['trip_id']}: {e}")
        raise

@transaction.atomic
def load_shapes():
    try:
        # Deleting all records from the table

        ShapeId.objects.all().delete()
        Shape.objects.all().delete()
        
        # Checking GTFS-ZTM existence
        if not os.path.exists(GTFS_DIR):
            raise FileNotFoundError(f"Directory {GTFS_DIR} doesn't exist.")
        
        # Checking that the file exists
        file_path = os.path.join(GTFS_DIR, 'shapes.txt')
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} doesn't exist.")
        
        # Loading data from CSV
        with open(file_path, 'r',encoding='utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            shapes_data = list(csv_reader)
            shape_ids = set(row['shape_id'] for row in shapes_data)

            for shape_id in shape_ids:
                shape_id_obj = ShapeId.objects.create(shape_id=shape_id)

                shape_points = [row for row in shapes_data if row['shape_id'] == shape_id]
                
                for row in shape_points:
                    Shape.objects.create(
                        shape_id=shape_id_obj,
                        shape_pt_lat=row['shape_pt_lat'],
                        shape_pt_lon=row['shape_pt_lon'],
                        shape_pt_sequence=row['shape_pt_sequence'],
                    )
        print("Shapes loaded successfully.")

        
    except Exception as e:
        print(f"There was an error: {e}")
        raise

@transaction.atomic
def load_feed_info():
    try:
        # Deleting all records from table
        FeedInfo.objects.all().delete()
        
        # Checking GTFS-ZTM exist
        if not os.path.exists(GTFS_DIR):
            raise FileNotFoundError(f"Directory {GTFS_DIR} doesn't exist.")
        
        # Checking that file exist
        file_path = os.path.join(GTFS_DIR, 'feed_info.txt')
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} doesn't exist.")
        
        # Loading files from CSV
        with open(file_path,'r', encoding='utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                
                feed_start_date = datetime.strptime(row['feed_start_date'], '%Y%m%d').strftime('%Y-%m-%d')
                feed_end_date = datetime.strptime(row['feed_end_date'], '%Y%m%d').strftime('%Y-%m-%d')
                
                
                FeedInfo.objects.create(
                    feed_publisher_name=row['feed_publisher_name'],
                    feed_publisher_url=row['feed_publisher_url'],
                    feed_lang=row['feed_lang'],
                    feed_start_date=feed_start_date,
                    feed_end_date=feed_end_date,
                )
        print("Feed info loaded successfully.")
    
    except Exception as e:
        print(f"There was an error: {e}")
        raise

@transaction.atomic
def load_calendar():
    try:
        # Deleting all records from table
        Calendar.objects.all().delete()
        
        # Checking GTFS-ZTM exist
        if not os.path.exists(GTFS_DIR):
            raise FileNotFoundError(f"Directory {GTFS_DIR} doesn't exist.")
        
        # Checking that file exist
        file_path = os.path.join(GTFS_DIR, 'calendar.txt')
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} doesn't exist.")
        
        # Loading files from CSV
        with open(file_path,'r',encoding='utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
            
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

        print("Calendar loaded successfully.")

    except Exception as e:
        print(f"There was an error: {e}")
        raise


# Import data
load_agency()
load_stops()
load_routes()
load_shapes()
load_calendar()
load_feed_info()
load_trips()
load_stop_times()
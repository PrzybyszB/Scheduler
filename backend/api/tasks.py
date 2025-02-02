import requests
import json
import io
import os
import hashlib
import csv
import logging
import pandas as pd
import requests
from datetime import datetime
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from google.protobuf.message import DecodeError
from redis.exceptions import RedisError
from google.transit import gtfs_realtime_pb2
from celery import shared_task
from .services.trip_detail import fetch_and_save_trip_detail
from .services.get_schedule import get_schedule_for_day
from .services.gtfs_processing import GTFSService
from .services.stop_detail import get_route_ids_on_stop_for_redis, create_stops_dict

logger = logging.getLogger('api')

gtfs_services = GTFSService()

@shared_task
def check_and_fetch_RT_file(url, key):
        
    try:
        response = requests.get(url)
        
        # Parsing new file from url
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        if feed.HasField('header'):
            header = feed.header
            new_file_timestamp = header.timestamp
        else:
            print("There is no header in new file")
            return
        
        print(f"New file timestamp for {key}: {new_file_timestamp}")

        # Looking for file in Redis db
        old_file = gtfs_services.client.get(key)
        
        # Downlad if doesn't exist
        if old_file is None or old_file == b'':
            old_file = gtfs_services.fetch_and_convert_pb_to_json(url, key)
            print(f"Downloaded file {key} to Redis")

        # Parsing data from Redis 
        json_data = json.loads(old_file)
        old_file_timestamp = int(json_data['header']['timestamp'])
        print(f"Old file timestamp for {key}: {old_file_timestamp}")

        if new_file_timestamp != old_file_timestamp:
            gtfs_services.fetch_and_convert_pb_to_json(url, key)
        else:
            print(f"File {key} is up to date")
    
    except requests.exceptions.RequestException as e:
        print(f"Error while downloading file from URL: {e}")
    
    except DecodeError as e:
        print(f"Error while parsing file: {e}")
    
    except RedisError as e:
        print(f"Error while work with Redis: {e}")
    
    except json.JSONDecodeError as e:
        print(f"Error while parsing JSON: {e}")
    
    except KeyError as e:
        print(f"Key error while accessing JSON data: {e}")
    
    except Exception as e:
        print(f"Unexpected error: {e}")

@shared_task
def check_and_fetch_static_file(url, zip_name):
    try:
        response = requests.get(url)
        response.raise_for_status()
        ttl_in_seconds = 7 * 24 * 3600


        # Getting content-disposition
        content_disposition = response.headers.get('content-disposition')

        # Check if the content_disposition header is available.
        if content_disposition:

            # If header is available, extract the filename from it
            zip_name = gtfs_services.get_filename_from_content_disposition(content_disposition)
        else:

            # If header is not available, extract the filename from url 
            zip_name = os.path.basename(url).split('?')[0]
        
        # Checking hash of zip file to know if a new one needs to be downloaded
        new_file_hash = hashlib.md5(response.content).hexdigest()
        stored_file_hash = gtfs_services.client.get(f"{zip_name}:hash")


        if not stored_file_hash:  

            # Store the file name, hash for zip and data inside
            gtfs_services.process_file(response.content, zip_name)
            gtfs_services.client.setex(zip_name, ttl_in_seconds, response.content)
            gtfs_services.client.setex(f"{zip_name}:hash", ttl_in_seconds, new_file_hash)
            print(f"Downloaded file {zip_name} and set new hash {new_file_hash}")
            return True

        print(f"Stored file hash is {stored_file_hash.decode('utf-8')}")

        if stored_file_hash.decode('utf-8') != new_file_hash:
            gtfs_services.process_file(response.content, zip_name)
            gtfs_services.client.setex(zip_name, ttl_in_seconds, response.content)
            gtfs_services.client.setex(f"{zip_name}:hash", ttl_in_seconds, new_file_hash)
            print(f"Downloaded and updated file {zip_name}")
            return True

        else:
            print(f"Static ZIP file {zip_name} is already up-to-date.")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Error while downloading file from URL: {e}")

    except RedisError as e:
        print(f"Error while working with Redis: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")

# ----------------------------------Prrocess data to redis---------------------------------------
@shared_task
def process_trip_detail():
    '''
    Main function to process trip data and save route details in Redis.
    '''
    try:
        # Retrieving unique route_id from Redis
        active_route_ids = gtfs_services.client.smembers("active:route_ids")

        # Process each active routes
        for route_id in active_route_ids:
            route_id = route_id.decode('utf-8')
            fetch_and_save_trip_detail(route_id)

        print("Active routes data was successfully process")

    except Exception as e:
        return {"error": str(e)}

@shared_task
def create_active_routes():
    """
    Creating set of active_routes and save it to Redis.
    """
    try:
        if gtfs_services.client.exists("active:route_ids"):
            gtfs_services.client.delete("active:route_ids")
            print("Deleted existing active:route_ids set.")

        trips_data = gtfs_services.client.get('trips.txt')
        if not trips_data:
            raise ValueError('Lack of trips.txt data in Redis')
        
        trips_csv = csv.DictReader(io.StringIO(trips_data.decode('utf-8')))

        for trip in trips_csv:
            route_id = trip['route_id']

            # Creating set in redis of active_routes
            if not gtfs_services.client.sismember("active:route_ids", route_id):
                gtfs_services.client.sadd("active:route_ids", route_id)
                print(f"Added route_id {route_id}")

    except Exception as e:
        print(f"There was an error: {e}")
        raise

@shared_task
def create_active_stop_id():
    """
    Creating set of active_stops and assign stop details, then save it to Redis.
    """
    try:
        if gtfs_services.client.exists("active:stop_ids"):
            gtfs_services.client.delete("active:stop_ids")
            print("Deleted existing active:stop_ids set.")

        stops_data = gtfs_services.client.get('stops.txt')
        if not stops_data:
            raise ValueError('Lack of stops.txt data in Redis')
        
        stops_csv = csv.DictReader(io.StringIO(stops_data.decode('utf-8')))

        # Create the stops dictionar
        stops_dict = create_stops_dict(stops_csv)

        for stop_id, stop_details in stops_dict.items():
            
            if not gtfs_services.client.sismember("active:stop_ids", stop_id):
                gtfs_services.client.sadd("active:stop_ids", stop_id)
                redis_key = f"stop_details:{stop_id}"
                gtfs_services.client.hset(redis_key, mapping=stop_details)

                print(f"Added stop_id {stop_id} with details")
            
            try:
                # Extracting the route_ids of circulating buses for a stop 
                route_data = get_route_ids_on_stop_for_redis(stop_id)

                # Saving routes in redis
                route_redis_key = f"routes_for_stop:{stop_id}"
                gtfs_services.client.set(route_redis_key, json.dumps(route_data))

                print(f"Saved routes for stop_id {stop_id}")

            except Exception as e:
                print(f"Error processing routes for stop_id {stop_id}: {e}")

    except Exception as e:
        print(f"There was an error: {e}")
        raise

@shared_task
def save_schedules_to_redis():
    """
    Saving schedules by day to redis
    """
    try:
        # Process schedule
        get_schedule_for_day()

        print(f"Fetched schedules by day done")

    except Exception as e:
        print(f"An error occurred: {e}")

#---------------------------------------Load to DB-------------------------------------------------
@shared_task 
@transaction.atomic
def load_agency():
    from api.models import Agency

    try:
        # Deleting all records from table
        Agency.objects.all().delete()
        
        agency_data = gtfs_services.client.get('agency.txt')
        if not agency_data:
            raise ValueError('Lack of agency.txt data in Redis')
        
        csv_file = io.StringIO(agency_data.decode('utf-8'))
        
        csv_reader = csv.DictReader(csv_file)
        
        for row in csv_reader:
            Agency.objects.create(
                agency_id=row['agency_id'],
                agency_name=row['agency_name'],
                agency_url=row['agency_url'],
                agency_timezone=row['agency_timezone'],
                agency_phone=row['agency_phone'],
                agency_lang=row['agency_lang']
            )
        
        print("Agency loaded successfully ")
    
    except Exception as e:
        print(f"There was an error: {e}")
        raise

@shared_task
@transaction.atomic
def load_stops():
    from api.models import Stop

    try:
        # Deleting all records from table
        Stop.objects.all().delete()

        stops_data = gtfs_services.client.get('stops.txt')
        if not stops_data:
            raise ValueError('Lack of stops.txt data in Redis')
        
        csv_file = io.StringIO(stops_data.decode('utf-8'))
        
        csv_reader = csv.DictReader(csv_file)

        # Create empty set for redis
        stop_ids = []

        for row in csv_reader:
            Stop.objects.create(

                stop_id=row['stop_id'],
                stop_code=row['stop_code'],
                stop_name=row['stop_name'],
                stop_lat=row['stop_lat'],
                stop_lon=row['stop_lon'],
                zone_id=row['zone_id'],
            )
            stop_id = row["stop_id"]
            stop_data = {
                'stop_code': row['stop_code'],
                'stop_name': row['stop_name'],
                "stop_lat": row["stop_lat"],
                "stop_lon": row["stop_lon"],
                "zone_id": row["zone_id"]
        }
            gtfs_services.client.hset(f"stop:{stop_id}", mapping=stop_data)

            stop_ids.append(stop_id)
        
        # Save list stops to redis set with key all_stops
        gtfs_services.client.sadd("all_stops", *stop_ids)

        print("Stops loaded successfully.")

    
    except Exception as e:
        print(f"There was an error: {e}")
        raise

@shared_task
@transaction.atomic
def load_routes():
    from api.models import Route, Agency

    try:
        # Deleting all records from table
        Route.objects.all().delete()

        routes_data = gtfs_services.client.get('routes.txt')
        if not routes_data:
            raise ValueError('Lack of routes.txt data in Redis')
        
        csv_file = io.StringIO(routes_data.decode('utf-8'))
        
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            # Fetch agency by ID
            agency = Agency.objects.get(agency_id=row['agency_id'])

        
            Route.objects.create(
                route_id=row['route_id'],
                agency_id=agency,
                route_short_name=row['route_short_name'],
                route_long_name=row['route_long_name'],
                route_desc=row['route_desc'],
                route_type=row['route_type'],
                route_color=row['route_color'],
                route_text_color=row['route_text_color']

            )

        print("Routes loaded successfully.")
    
    except Exception as e:
        print(f"There was an error: {e}")
        raise

@shared_task
@transaction.atomic
def load_trips():
    '''
    I need to skip the missing objects because they have been missing data (in calendar_dates.txt), multiple times since I started working on this app. I mailed them, and their response was an apology for the inconvenience caused by the missing data.
    '''

    from api.models import Trip, Calendar, Route, Shape, ShapeId

    try:
        # Deleting all records from table
        Trip.objects.all().delete()

        trips_data = gtfs_services.client.get('trips.txt')
        if not trips_data:
            raise ValueError('Lack of trips.txt data in Redis')
        
        csv_file = io.StringIO(trips_data.decode('utf-8'))
        
        csv_reader = csv.DictReader(csv_file)
        
        for row in csv_reader:
            try:

                # Fetch calendar, route, shape, shapeid by ID
                service = Calendar.objects.get(service_id=row['service_id'])
                route = Route.objects.get(route_id=row['route_id'])
                shape_id = ShapeId.objects.get(shape_id=row['shape_id'])
                shape = Shape.objects.filter(shape_id=shape_id).first()
            
            # Skipping row due to missing related object
            except ObjectDoesNotExist as e:
                continue
            
            Trip.objects.create(
                    route_id=route,
                    service_id=service,
                    trip_id=row['trip_id'],
                    trip_headsign=row['trip_headsign'],
                    direction_id=row['direction_id'],
                    shape=shape,
                    wheelchair_accessible=row['wheelchair_accessible'],
                    brigade=row['brigade'],
            )
        print("Trips loaded successfully.")
    
    except Exception as e:
        print(f"There was an error: {e}")
        raise

@shared_task
@transaction.atomic
def load_stop_times():

    '''
    Due to missing data in calendar_dates.txt, I have to skip data in load_trips and then i load_stop_times
    '''

    from api.models import StopTime, Trip, Stop

    try:
        # Deleting all records from table
        StopTime.objects.all().delete()

        stop_times_data = gtfs_services.client.get('stop_times.txt')
        if not stop_times_data:
            raise ValueError('Lack of stop_times.txt data in Redis')
        
        csv_file = io.StringIO(stop_times_data.decode('utf-8'))
        
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            try:
                trip = Trip.objects.get(trip_id=row['trip_id'])
                arrival_time = gtfs_services.convert_time(row['arrival_time'])
                departure_time = gtfs_services.convert_time(row['departure_time'])
                stop = Stop.objects.get(stop_id=row['stop_id'])

            # Skipping row due to missing related object
            except ObjectDoesNotExist as e:
                continue

            StopTime.objects.create(
                trip_id=trip,
                arrival_time=arrival_time,
                departure_time=departure_time,
                stop_id=stop,
                stop_sequence=row['stop_sequence'],
                stop_headsign=row['stop_headsign'],
                pickup_type=row['pickup_type'],
                drop_off_type=row['drop_off_type'],
            )

        print("Stop times loaded successfully.")
    
    except Exception as e:
        print(f"There was an error: {e}")
        raise

@shared_task
@transaction.atomic
def load_shapes():
    from api.models import Shape, ShapeId

    try:
        # Deleting all records from table
        ShapeId.objects.all().delete()
        Shape.objects.all().delete()

        shapes_data = gtfs_services.client.get('shapes.txt')
        if not shapes_data:
            raise ValueError('Lack of shapes.txt data in Redis')
        
        csv_file = io.StringIO(shapes_data.decode('utf-8'))
        
        csv_reader = csv.DictReader(csv_file)
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

@shared_task
@transaction.atomic
def load_feed_info():
    from api.models import FeedInfo

    try:
        # Deleting all records from table
        FeedInfo.objects.all().delete()

        feed_info_data = gtfs_services.client.get('feed_info.txt')
        if not feed_info_data:
            raise ValueError('Lack of feed_info.txt data in Redis')
        
        csv_file = io.StringIO(feed_info_data.decode('utf-8'))
        
        csv_reader = csv.DictReader(csv_file)

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

@shared_task
@transaction.atomic
def load_calendar():
    from api.models import Calendar

    try:
        # Deleting all records from table
        Calendar.objects.all().delete()

        calendar_data = gtfs_services.client.get('calendar.txt')
        if not calendar_data:
            raise ValueError('Lack of calendar.txt data in Redis')
        
        csv_file = io.StringIO(calendar_data.decode('utf-8'))
        
        csv_reader = csv.DictReader(csv_file)

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

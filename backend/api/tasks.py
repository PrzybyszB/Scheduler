import requests
import redis
import json
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToJson
from celery import Celery
from celery import shared_task


# app = Celery('tasks', broker='redis://0.0.0.0:6379/0', backend='redis://0.0.0.0:6379/0')

client = redis.Redis(host='redis')

URL_RT_1 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=trip_updates.pb'
URL_RT_2 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=feeds.pb'
URL_RT_3 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=vehicle_positions.pb'



@shared_task
def check_file(url, key):
        response = requests.get(url)
        
        # Parsing new file from url
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        if feed.HasField('header'):
            header = feed.header
            new_file_timestamp = header.timestamp
        print(f"New file timestamp for {key}: {new_file_timestamp}")

        # Looking for file in Redis db
        old_file = client.get(key)
        
        # Downlad if doesn't exist
        if old_file is None or old_file == b'':
            old_file = fetch_and_convert_pb_to_json(url, key)
            print(f"Downloaded file {key} to Redis")

        # Parsing data from Redis 
        json_data = json.loads(old_file)
        old_file_timestamp = int(json_data['header']['timestamp'])
        print(f"Old file timestamp for {key}: {old_file_timestamp}")

        if new_file_timestamp != old_file_timestamp:
             fetch_and_convert_pb_to_json(url, key)
        else:
            print(f"File {key} is up to date")

@shared_task
def fetch_and_convert_pb_to_json(url, key):
    response = requests.get(url)
    response.raise_for_status()

    # Create feed message object
    feed = gtfs_realtime_pb2.FeedMessage()
    
    # Parsing HTTP response content into object FeedMessage
    feed.ParseFromString(response.content)
    
    # Convert protobuf object into JSON format(but its string)
    json_data_format = MessageToJson(feed)

    # Saving file into Redis with unique key
    client.set(key, json_data_format)
    print(f"File: {key} downloaded")
    
    return json_data_format

# Check file
# trip_updates_data_check = check_file(URL_RT_1, 'trip_updates')
# feeds_data_check = check_file(URL_RT_2, 'feeds')
# vehicle_positions_data_check = check_file(URL_RT_3, 'vehicle_positions')

# # Redis JSON format data
# trip_updates_data = fetch_and_convert_pb_to_json(URL_RT_1, 'trip_updates')
# feeds_data = fetch_and_convert_pb_to_json(URL_RT_2, 'feeds')
# vehicle_positions_data = fetch_and_convert_pb_to_json(URL_RT_3, 'vehicle_positions')

# # JSON data
# trip_updates_json = json.loads(trip_updates_data)
# feeds_json = json.loads(feeds_data)
# vehicle_positions_json = json.loads(vehicle_positions_data)

'''
List of expect

requests.exceptions.ChunkedEncodingError: ('Connection broken: IncompleteRead(26627 bytes read, 64 more expected)', IncompleteRead(26627 bytes read, 64 more expected))

'''


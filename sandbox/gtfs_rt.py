import json
import os
import requests
import shutil
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToJson

GTFS_DIR_RT = 'api/GTFS-ZTM/GTFS-ZTM-RT'

# URLs for files
URL_RT_1 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=trip_updates.pb'
URL_RT_2 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=feeds.pb'
URL_RT_3 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=vehicle_positions.pb'
URL_RT_4 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=vehicle_dictionary.csv'

FILE_PATH_RT_1 = os.path.join(GTFS_DIR_RT, 'trip_update.pb')
FILE_PATH_RT_2 = os.path.join(GTFS_DIR_RT, 'feeds.pb')
FILE_PATH_RT_3 = os.path.join(GTFS_DIR_RT, 'vehicle_positions.pb')
FILE_PATH_RT_4 = os.path.join(GTFS_DIR_RT, 'vehicle_dictionary.csv')

def clear_directory():
    if os.path.exists(GTFS_DIR_RT):
        for file in os.listdir(GTFS_DIR_RT):
            file_path = os.path.join(GTFS_DIR_RT, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

def download_file(url, file_path):
    response = requests.get(url)
    response.raise_for_status()
    with open(file_path, 'wb') as f:
        f.write(response.content)

def read_pb_file(file_path):
    with open(file_path, "rb") as f:
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(f.read())
        return feed

def convert_pb_to_json(pb_file_path, json_file_path):
    feed = read_pb_file(pb_file_path)
    json_data = MessageToJson(feed)
    with open(json_file_path, "w") as f:
        f.write(json_data)

def run():
    urls_and_paths = [
        (URL_RT_1, FILE_PATH_RT_1),
        (URL_RT_2, FILE_PATH_RT_2),
        (URL_RT_3, FILE_PATH_RT_3),
        (URL_RT_4, FILE_PATH_RT_4)
    ]
    
    clear_directory()

    for url, file_path in urls_and_paths:
        download_file(url, file_path)
    
    pb_files = [FILE_PATH_RT_1, FILE_PATH_RT_2, FILE_PATH_RT_3]

    trip_update_json = os.path.join(GTFS_DIR_RT, 'trip_update.json')
    feeds_json = os.path.join(GTFS_DIR_RT, 'feeds.json')
    vehicle_positions_json = os.path.join(GTFS_DIR_RT, 'vehicle_positions.json')
    
    json_files = [trip_update_json, feeds_json, vehicle_positions_json]
    
    for pb_file, json_file in zip(pb_files, json_files):
        convert_pb_to_json(pb_file, json_file)
    
    data = {}
    for json_file in json_files:
        with open(json_file, 'r') as file:
            data[json_file] = json.load(file)

    trip_update_data = data[trip_update_json]
    vehicle_positions_data = data[vehicle_positions_json]

    for entity_vehicle in vehicle_positions_data['entity']:
        vehicle = entity_vehicle['vehicle']
        trip = vehicle['trip']
        route_id = trip['routeId']
        position = vehicle['position']
        
        if route_id == "16":
            for entity_trip in trip_update_data['entity']:
                trip_update = entity_trip['tripUpdate']
                trip = trip_update['trip']
                trip_route_id = trip['routeId']
                
                if trip_route_id == "16":
                    stopTimeUpdate = trip_update['stopTimeUpdate']
                    for stop_update in stopTimeUpdate:
                        arrival = stop_update['arrival']
                        delay = arrival['delay']
                        if entity_vehicle['id'] == entity_trip['id']:
                            print(f"Entity: {entity_vehicle['id']}, Route ID: {route_id}, Position: {position}, Delay: {delay}")
                            break



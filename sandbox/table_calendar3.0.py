import gtfs_kit as gk
import pandas as pd
import redis
import json
import re
import tempfile
import os
from datetime import datetime
import zipfile
import io

client = redis.Redis(host='172.19.0.2')
DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

def process_file(file_content, zip_name):

    with zipfile.ZipFile(io.BytesIO(file_content)) as z:
        for file_name in z.namelist():

            with z.open(file_name) as f:
                file_content = f.read()

                # Deleting Byte Order Mark
                file_content = file_content.lstrip(b'\xef\xbb\xbf')
                
                decoded_file = file_content.decode('utf-8')
                
                ttl_in_seconds = 15 * 24 * 3600
                client.setex(file_name, ttl_in_seconds, decoded_file)
                    
                print(f'File {file_name} stored')

def extract_date_from_filename(filename):
    '''
    Extract date from the filename (e.g., '20240907_20240930.zip')
    '''
    try:
        date_str = filename.split('_')[0]

        # Convert string to date object
        return datetime.strptime(date_str, '%Y%m%d')
    except ValueError:

        # If the date format is invalid, skip this file
        return None  

def fetch_gtfs_files_from_redis():
    '''
    Fetches all keys from Redis, filters out keys ending with ':hash', decodes them to strings, and returns the list of remaining keys.
    '''
    try:
        all_keys = client.keys('*')
        gtfs_keys = []
        
        for key in all_keys:
            decoded_key = key.decode('utf-8')
            
            if decoded_key.endswith('.zip'):
                gtfs_keys.append(decoded_key)
            # Delete this 
            # if not decoded_key.endswith(':hash'):
            #     gtfs_keys.append(decoded_key)

        return gtfs_keys
    
    except Exception as e:
        return {'error': 'There was an error ' + str(e)}

def load_gtfs_feed_from_redis(filename):
    '''
    Use a temporary file to handle the GTFS data using gtfskit
    '''

    try:
        file_content = client.get(filename)
        if file_content:

            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            try:

                # Load GTFS data from the temporary file
                feed = gk.feed.read_feed(path_or_url=temp_file_path, dist_units='km')
                return feed
            except Exception as e:
                return {'error': f'Error loading GTFS feed from {temp_file_path}: {e}'}
            finally:

                # Remove the temporary file
                os.remove(temp_file_path)
        else:
            return {'error': f'File {filename} not found in Redis.'}
    except Exception as e:
        return {'error': f'Error loading GTFS feed from Redis: {e}'}    

def convert_time(departure_time):
    '''
    Night routes have time 24:00, 25:00, 26:00, 27:00, 28:00
    '''
    try:
        pattern = re.compile(r"(2[4-9]):([0-5][0-9])")
        match = pattern.match(departure_time)
        if match:
            hour = int(match.group(1))
            new_hour = hour - 24
            return f"{new_hour}:{match.group(2)}"
        
        return departure_time
    except Exception as e:
        raise ValueError(f"Error converting time '{departure_time}': {e}")


gtfs_files = fetch_gtfs_files_from_redis()

if not gtfs_files:
    raise ValueError("No GTFS files available in Redis.")

# Filter and sort GTFS files based on date extracted from filename
gtfs_files_filtered = [
    file for file in gtfs_files if extract_date_from_filename(file) is not None
]
gtfs_files_sorted = sorted(gtfs_files_filtered, key=extract_date_from_filename, reverse=True)

for gtfs_file in gtfs_files_sorted:
    feed = load_gtfs_feed_from_redis(gtfs_file)

    if not feed:
        continue

    calendar_df = feed.calendar
    trips_df = feed.trips
    stop_times_df = feed.stop_times
    stops_df = feed.stops

    days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

    route_id = "250"
    direction_id = "0"
    stop_id = "1757"

    for day in days_of_week:

        day_services = calendar_df[calendar_df[day] == 1]

        start_date = calendar_df[['start_date']]
        end_date = calendar_df[['end_date']]

        print(start_date)

        trips_on_day = pd.merge(day_services, trips_df, on='service_id')
        stop_times_on_day = pd.merge(trips_on_day, stop_times_df, on='trip_id')
        full_schedule = pd.merge(stop_times_on_day, stops_df, on='stop_id')

        route_ids = client.smembers("active:route_ids")

        for route_id in route_ids:
            route_id = route_id.decode('utf-8')

        # Filter the schedule by route_id
            full_schedule_filtered = full_schedule[full_schedule['route_id'] == route_id]

            file_index = gtfs_files_sorted.index(gtfs_file)

            while full_schedule_filtered.empty and file_index < len(gtfs_files_sorted) - 1:
                file_index += 1
                next_file = gtfs_files_sorted[file_index]
                print(f"No data found in {gtfs_file} for route {route_id}. Trying {next_file}...")
                next_feed = load_gtfs_feed_from_redis(next_file)

                if not next_feed:
                    continue

                # Przetwórz kolejną paczkę
                calendar_df = next_feed.calendar
                trips_df = next_feed.trips
                stop_times_df = next_feed.stop_times
                stops_df = next_feed.stops

                day_services = calendar_df[calendar_df[day] == 1]
                trips_on_day = pd.merge(day_services, trips_df, on='service_id')
                stop_times_on_day = pd.merge(trips_on_day, stop_times_df, on='trip_id')
                full_schedule = pd.merge(stop_times_on_day, stops_df, on='stop_id')
                full_schedule_filtered = full_schedule[full_schedule['route_id'] == route_id]

            if full_schedule_filtered.empty:
                
                # Create an empty DataFrame with specified columns
                empty_schedule = pd.DataFrame({
                    'route_id': [route_id],
                    'stop_id': [None],
                    'direction_id': [None],
                    'departure_time': [None],
                    'stop_headsign': [None],
                    'start_date': start_date.iloc[0, 0],
                    'end_date': end_date.iloc[0, 0]
                })
                
                schedule_json = empty_schedule.to_json(orient='records')
                
                redis_key = f"route_{route_id}_schedule_for_{day}"
                client.set(redis_key, schedule_json)
                continue

            # Prepare the final DataFrame for the selected route
            final_df = full_schedule_filtered[[
                'route_id', 'departure_time', 'start_date', 'end_date' , 'stop_id', 'direction_id', 'trip_id', 'stop_headsign', 'stop_name'
            ]].sort_values(by=['stop_id', 'direction_id', 'departure_time'])

            # Convert times for night routes
            final_df['departure_time'] = final_df['departure_time'].apply(convert_time).str.slice(0, 5)

            grouped_schedule = final_df[['departure_time', 'stop_name', 'stop_id' , 'direction_id' , 'stop_headsign','end_date', 'start_date']]

            schedule_json = grouped_schedule.to_json(orient='records')
            redis_key = f"route_{route_id}_schedule_for_{day}"
            client.set(redis_key, schedule_json)


            print(f"Route ID: {route_id} Day: {day}")
            # print(f"Grouped schedule {grouped_schedule}")

redis_key = f"route_{route_id}_schedule_for_sunday"
data = client.get(redis_key)

if data:
    decoded_data = data.decode('utf-8')
    json_data = json.loads(decoded_data) 
    
    schedule = []

    for item in json_data:
        item_stop_id = item['stop_id']
        item_direction_id = item['direction_id']
        stop_headsign = item['stop_headsign']
        if item_stop_id == stop_id:
            if str(item_direction_id) == direction_id:
                departure_time = item['departure_time']
else:
    print("No data found in Redis.")
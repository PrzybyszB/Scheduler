import gtfs_kit as gk
import pandas as pd
import redis
import json
import re
import csv
import io

client = redis.Redis(host='172.19.0.3')
DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

def get_active_stop_names(stop_id):
    '''
    Fetch the name of a stop based on its stop_id from the Redis hash 'active:stop_names'
    '''
    try:
        stop_name = client.hget("active:stop_names", stop_id)
        if stop_name:
            return stop_name.decode('utf-8')
        else:
            return {'error': f'Stop_id {stop_id} not found in Redis'}
    except Exception as e:
        return {'error': f'Error fetching stop_name from Redis: {e}'}

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


path_to_gtfs = '20250106_20250125.zip'
feed = gk.feed.read_feed(path_or_url=path_to_gtfs, dist_units='km')

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

    trips_on_day = pd.merge(day_services, trips_df, on='service_id')
    stop_times_on_day = pd.merge(trips_on_day, stop_times_df, on='trip_id')
    full_schedule = pd.merge(stop_times_on_day, stops_df, on='stop_id')

    direction_id = '0'
    stop_id = '221'
    route_id = '16'
    route_ids = client.smembers("active:route_ids")

    for route_id in route_ids:
        route_id = route_id.decode('utf-8')

    # Filter the schedule by route_id
        full_schedule_filtered = full_schedule[full_schedule['route_id'] == route_id]
        if full_schedule_filtered.empty:
            
            # Create an empty DataFrame with specified columns
            empty_schedule = pd.DataFrame({
                'route_id': [route_id],
                'stop_id': [None],
                'direction_id': [None],
                'departure_time': [None],
                'stop_headsign': [None]  
            })
            
            schedule_json = empty_schedule.to_json(orient='records')
            
            redis_key = f"route_{route_id}_schedule_for_{day}"
            client.set(redis_key, schedule_json)
            print(f"{redis_key} saved as an empty schedule with route_id {route_id}.")
            continue

        # Prepare the final DataFrame for the selected route
        final_df = full_schedule_filtered[[
            'route_id', 'departure_time', 'start_date', 'stop_id', 'direction_id', 'trip_id', 'stop_headsign', 'stop_name'
        ]].sort_values(by=['stop_id', 'direction_id', 'departure_time'])

        # Convert times for night routes
        final_df['departure_time'] = final_df['departure_time'].apply(convert_time).str.slice(0, 5)

        grouped_schedule = final_df[['departure_time', 'stop_name', 'stop_id' , 'direction_id' , 'stop_headsign',]]

        schedule_json = grouped_schedule.to_json(orient='records')
        print(schedule_json)
        redis_key = f"route_{route_id}_schedule_for_{day}"
        client.set(redis_key, schedule_json)


        print(f"Route ID: {route_id} Day: {day}")
        print(f"Grouped schedule {grouped_schedule}")

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
    print(departure_time)
else:
    print("No data found in Redis.")
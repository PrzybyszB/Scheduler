import re
import pandas as pd
from datetime import datetime
import json
import logging
from .gtfs_processing import GTFSService
from .trip_detail import get_trip_detail



logger = logging.getLogger('api')
gtfs_service = GTFSService()
DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

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

def get_valid_day_of_week(day_of_week=None):
    '''
    Function return day of week or actual day of week for schedule
    '''
    try:
        if day_of_week is not None:
            if day_of_week not in DAYS_OF_WEEK:
                raise ValueError(f"Invalid day of the week. Valid values are: {', '.join(DAYS_OF_WEEK)}.")
        
        return day_of_week or DAYS_OF_WEEK[datetime.today().weekday()]
    except Exception as e:
        raise ValueError(f"Error validating day of the week: {e}")

def get_schedule_for_day():
    """
    Process GTFS data and retrieving schedules
    """
    try:
        # Fetch GTFS files from Redis
        gtfs_files = gtfs_service.fetch_gtfs_files_from_redis()

        if not gtfs_files:
            raise ValueError("No GTFS files available in Redis.")

        # Filter and sort GTFS files based on date extracted from filename
        gtfs_files_filtered = [
            file for file in gtfs_files if gtfs_service.extract_date_from_filename(file) is not None
        ]
        gtfs_files_sorted = sorted(gtfs_files_filtered, key=gtfs_service.extract_date_from_filename, reverse=True)

        for gtfs_file in gtfs_files_sorted:
            feed = gtfs_service.load_gtfs_feed_from_redis(gtfs_file)

            if not feed:
                continue

            for day in DAYS_OF_WEEK:
                
                # Extract dataframes from GTFS feed
                calendar_df = feed.calendar
                trips_df = feed.trips
                stop_times_df = feed.stop_times
                stops_df = feed.stops

                day_services = calendar_df[calendar_df[day] == 1]

                trips_on_day = pd.merge(day_services, trips_df, on='service_id')
                stop_times_on_day = pd.merge(trips_on_day, stop_times_df, on='trip_id')
                full_schedule = pd.merge(stop_times_on_day, stops_df, on='stop_id')
                

                route_ids = gtfs_service.client.smembers("active:route_ids")

                for route_id in route_ids:
                    route_id = route_id.decode('utf-8')

                    # Filter the schedule by route_id
                    full_schedule_filtered = full_schedule[full_schedule['route_id'] == route_id]

                    # Check if data is avalible, if not create empty one
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
                        gtfs_service.client.set(redis_key, schedule_json)
                        print(f"{redis_key} saved as an empty schedule with route_id {route_id}.")
                        continue

                    # Prepare the final DataFrame for the selected route
                    final_df = full_schedule_filtered[[
                        'route_id', 'departure_time', 'start_date', 'stop_id', 'direction_id', 'trip_id', 'stop_headsign', 'stop_name'
                    ]].sort_values(by=['stop_id', 'direction_id', 'departure_time'])

                    # Convert times for night routes
                    final_df['departure_time'] = final_df['departure_time'].apply(convert_time).str.slice(0, 5)

                    grouped_schedule = final_df[['departure_time', 'stop_name', 'stop_id' , 'direction_id' ,  'stop_headsign']]

                    schedule_json = grouped_schedule.to_json(orient='records')

                    redis_key = f"route_{route_id}_schedule_for_{day}"
                    gtfs_service.client.set(redis_key, schedule_json)
                    print(f"{redis_key} was sucessfully saved")

            return schedule_json
    except Exception as e:
        raise RuntimeError(f"Error retrieving schedule for day: {e}")

def get_trip_headsign(route_id, direction_id):
    '''
    Fetch trip_detail data for trip_headsign
    '''
    try:
        trip_headsign_data = get_trip_detail(route_id)
        most_popular_patterns = trip_headsign_data["most_popular_patterns"]

        for pattern_direction_id, pattern_data  in most_popular_patterns.items():
            if pattern_direction_id == direction_id:
                trip_headsign = pattern_data.get('trip_headsign')
                if trip_headsign:
                    return trip_headsign
        raise ValueError(f"There is no trip_headsign for :{most_popular_patterns}")
    
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None


def get_schedule_from_redis(route_id, stop_id, direction_id, day_of_week=None):
    '''
    Fetch data from redis and prepare final data
    '''
    try:
        day = get_valid_day_of_week(day_of_week)
        stop_name = gtfs_service.get_active_stop_names(stop_id)
        stop_headsign = get_trip_headsign(route_id, direction_id)
        redis_key = f"route_{route_id}_schedule_for_{day}"
        data = gtfs_service.client.get(redis_key)
        if data:
            schedule = []
            decoded_data = data.decode('utf-8')
            json_data = json.loads(decoded_data) 
            for item in json_data:
                item_stop_id = item['stop_id']
                item_direction_id = item['direction_id']
                if item_stop_id == stop_id:
                    if str(item_direction_id) == direction_id:
                        departure_time = item['departure_time']
                        schedule.append(departure_time)
            current_day_info = {
                'current_day': day,
                'schedule': schedule,
                'stop_name': stop_name,
                'stop_headsign': stop_headsign
                }
            return current_day_info
        else:
            print("No data found in Redis.")

    except Exception as e:
        raise RuntimeError(f"Error retrieving schedule from Redis: {e}")
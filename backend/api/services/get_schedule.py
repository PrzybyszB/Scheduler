import pandas as pd
from datetime import datetime
import json
import logging
from .gtfs_processing import GTFSService
from .trip_detail import get_trip_detail



logger = logging.getLogger('api')
gtfs_service = GTFSService()
DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

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

def load_routes_and_stops_from_redis():
    '''
    Fetches and caches all routes and stops from Redis once
    to avoid repeated requests to Redis within loops.
    '''
    try:
        # Get active routes and stops from Redis (only once)
        route_ids = gtfs_service.get_active_route_ids()
        stop_ids = gtfs_service.get_active_stop_ids()

        # Decode the data from Redis
        route_ids = [route_id.decode('utf-8') for route_id in route_ids]
        stop_ids = [stop_id.decode('utf-8') for stop_id in stop_ids]

        return route_ids, stop_ids
    except Exception as e:
        print(f"Error loading routes and stops from Redis: {e}")
        
        # Return empty lists in case of error
        return [], []

def get_schedule_for_day():
    """
    Process GTFS data and retrieving schedules by specific route_id and stop_id
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

        day_dataframes = {day: None for day in DAYS_OF_WEEK}

        route_ids, stop_ids = load_routes_and_stops_from_redis()

        # Loop through all available GTFS files
        for gtfs_file in gtfs_files_sorted:
            feed = gtfs_service.load_gtfs_feed_from_redis(gtfs_file)

            if not feed:
                continue
                
            # Extract dataframes from GTFS feed
            calendar_df = feed.calendar
            trips_df = feed.trips[['service_id', 'route_id', 'trip_id', 'direction_id', 'trip_headsign']]
            stop_times_df = feed.stop_times[['trip_id', 'departure_time', 'stop_id']]

            # List to store missing schedules for later processing
            missing_schedules = []

            for day_of_week in DAYS_OF_WEEK:
                if day_dataframes[day_of_week] is None:
                    active_services = calendar_df[calendar_df[day_of_week] == 1]

                    if not active_services.empty:
                        trips_on_day = pd.merge(active_services, trips_df, on='service_id')
                        full_schedule = pd.merge(trips_on_day, stop_times_df, on='trip_id')
                        
                        for stop_id in stop_ids:
                            route_ids = gtfs_service.get_route_ids_for_stop_schedule(stop_id)
                            
                            for route_id in route_ids:
                                filtered = full_schedule[(full_schedule['route_id'] == route_id) &
                                                        (full_schedule['stop_id'] == stop_id)]
                                
                                if not filtered.empty:

                                    # Prepare the final DataFrame for the selected route
                                    final_df = filtered[['route_id', 'departure_time', 'stop_id', 'direction_id', 'trip_id', 'trip_headsign', 'start_date', 'end_date']]
                                    final_df = final_df.sort_values(by=['stop_id', 'direction_id', 'departure_time'])

                                    # Convert departure times (adjusting for night schedules)
                                    final_df['departure_time'] = final_df['departure_time'].apply(gtfs_service.convert_time).str.slice(0, 5)

                                    grouped_schedule = final_df[['departure_time', 'stop_id', 'direction_id', 'start_date', 'end_date']]
                                    
                                    day_dataframes[day_of_week] = grouped_schedule

                                    schedule_json = grouped_schedule.to_json(orient='records')
                                    redis_key = f"route_{route_id}_stop_{stop_id}_schedule_for_{day_of_week}"
                                    gtfs_service.client.set(redis_key, schedule_json)
                                    print(f"Route ID: {route_id} Stop_id: {stop_id} Day: {day_of_week} as redis_key : {redis_key}")
                                else:
                                    missing_schedules.append((route_id, stop_id, day_of_week))
                                    print(f"Route ID: {route_id} Stop_id: {stop_id} Day: {day_of_week} added to empty list")

            # Now process missing schedules after checking all GTFS files
            for route_id, stop_id, day_of_week in missing_schedules:
                start_date = calendar_df['start_date'].iloc[0]
                end_date = calendar_df['end_date'].iloc[0]

                empty_schedule = pd.DataFrame({
                    'route_id': [None],
                    'stop_id': [stop_id],
                    'direction_id': [None],
                    'departure_time': [None],
                    'stop_headsign': [None],
                    'start_date': [start_date],
                    'end_date': [end_date]
                })
                
                # Save empty schedule to Redis for good view on every schedules
                schedule_json = empty_schedule.to_json(orient='records')
                redis_key = f"route_{route_id}_stop_{stop_id}_schedule_for_{day_of_week}"
                gtfs_service.client.set(redis_key, schedule_json)
                print(f"Route ID: {route_id} Stop_id: {stop_id} Day: {day_of_week} as empty")

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

        if stop_name is None:
            stop_name = {"error": f"Stop_id {stop_id} not found in Redis"}
        
        if stop_headsign is None:
            stop_headsign = None

        redis_key = f"route_{route_id}_stop_{stop_id}_schedule_for_{day}"
        data = gtfs_service.client.get(redis_key)
        if data:
            schedule = []
            decoded_data = data.decode('utf-8')
            json_data = json.loads(decoded_data) 
            for item in json_data:
                item_direction_id = item['direction_id']
                start_date = item['start_date']
                end_date = item['end_date']
                if str(item_direction_id) == direction_id:
                    departure_time = item['departure_time']
                    schedule.append(departure_time)
            current_day_info = {
                'current_day': day,
                'schedule': schedule,
                'stop_name': stop_name,
                'stop_headsign': stop_headsign,
                'start_date' : start_date,
                'end_date' : end_date
                }
            return current_day_info
        else:
            print("No data found in Redis.")

    except Exception as e:
        raise RuntimeError(f"Error retrieving schedule from Redis: {e}")
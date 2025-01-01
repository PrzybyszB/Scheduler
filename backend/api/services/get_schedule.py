import re
import pandas as pd
from datetime import datetime
from .gtfs_processing import GTFSService
import json
import logging

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
        DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
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

        schedules_by_day = {}

        for gtfs_file in gtfs_files_sorted:
            feed = gtfs_service.load_gtfs_feed_from_redis(gtfs_file)

            if not feed:
                continue

            # Extract dataframes from GTFS feed
            calendar_df = feed.calendar
            trips_df = feed.trips
            stop_times_df = feed.stop_times
            stops_df = feed.stops

            for day in DAYS_OF_WEEK:
                # Filter active services based on the current day
                day_services = calendar_df[calendar_df[day] == 1]

                # Merge dataframes to get the full schedule
                trips_on_day = pd.merge(day_services, trips_df, on='service_id')
                stop_times_on_day = pd.merge(trips_on_day, stop_times_df, on='trip_id')
                full_schedule = pd.merge(stop_times_on_day, stops_df, on='stop_id')

                # Serialized DataFrame to JSON
                full_schedule_json = full_schedule.to_json(orient='records')
                schedules_by_day[day] = full_schedule_json

        return schedules_by_day
    except Exception as e:
        raise RuntimeError(f"Error retrieving schedule for day: {e}")


def get_schedule_from_redis(route_id, stop_id, direction_id, day_of_week=None):
    '''
    Fetch data from redis and prepare final schedule
    '''
    try:
        current_day_of_week = get_valid_day_of_week(day_of_week)

        # Cast direction_id to an integer
        direction_id = int(direction_id)

        # Get data from Redis
        retrieved_data = gtfs_service.client.get(f"full_schedule_{current_day_of_week}")
        if not retrieved_data:
            raise ValueError(f"No schedule found for {current_day_of_week} in Redis.")

        retrieved_data_str = retrieved_data.decode('utf-8')

        # Make DataFrame from JSON
        retrieved_data_str = retrieved_data_str.replace('\\"', '"')
        retrieved_json = json.loads(retrieved_data_str)
        retrieved_df = pd.DataFrame(retrieved_json)

        # Creating expected Schedule with DataFrame
        full_schedule_filtered = retrieved_df[
            (retrieved_df['stop_id'] == stop_id) &
            (retrieved_df['route_id'] == route_id) &
            (retrieved_df['direction_id'] == direction_id)
        ]
        if full_schedule_filtered.empty:
            raise ValueError("No matching schedule found for the given parameters.")

        final_df = full_schedule_filtered[
            ['route_id', 'departure_time', 'start_date', 'stop_id', 'direction_id', 'trip_id', 'stop_headsign', 'stop_name']
        ].sort_values(by='departure_time')

        # Slicing seconds
        final_df['departure_time'] = final_df['departure_time'].apply(convert_time).str.slice(0, 5)
        stop_headsign = final_df['stop_headsign'].iloc[0]
        stop_name = final_df['stop_name'].iloc[0]

        current_day_info = {
            'current_day': current_day_of_week,
            'schedules': final_df.to_dict(orient='records'),
            'stop_name': stop_name,
            'stop_headsign': stop_headsign
        }
        return current_day_info
    except Exception as e:
        raise RuntimeError(f"Error retrieving schedule from Redis: {e}")
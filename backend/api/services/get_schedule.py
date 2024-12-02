import re
import pandas as pd
from datetime import datetime
from .gtfs_processing import GTFSService


gtfs_service = GTFSService()
DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

def convert_time(departure_time):
    '''
    Night routes have time 24:00, 25:00, 26:00, 27:00, 28:00
    '''
    pattern = re.compile(r"(2[4-9]):([0-5][0-9])")
    match = pattern.match(departure_time)
    if match:
        hour = int(match.group(1))
        new_hour = hour - 24
        return f"{new_hour}:{match.group(2)}"
    
    return departure_time

def get_valid_day_of_week(day_of_week=None):
    DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    if day_of_week is not None:
        if day_of_week not in DAYS_OF_WEEK:
            raise ValueError(f"Invalid day of the week. Valid values are: {', '.join(DAYS_OF_WEEK)}.")
    
    return day_of_week or DAYS_OF_WEEK[datetime.today().weekday()]

def get_schedule(route_id, stop_id, direction_id, day_of_week=None):
    
    current_day_of_week = get_valid_day_of_week(day_of_week)

    # Cast direction_id to an integer
    direction_id = int(direction_id)

    # Fetch GTFS files from Redis
    gtfs_files = gtfs_service.fetch_gtfs_files_from_redis()

    if not gtfs_files:
        raise ValueError("No GTFS files available in Redis.")

    # Filter and sort GTFS files based on date extracted from filename
    gtfs_files_filtered = []
    for file in gtfs_files:
        date = gtfs_service.extract_date_from_filename(file)

        if date is not None:
            gtfs_files_filtered.append(file)

    gtfs_files_sorted = sorted(gtfs_files_filtered, key=gtfs_service.extract_date_from_filename, reverse=True)

    day_dataframes = {}

    for day in DAYS_OF_WEEK:
        day_dataframes[day] = None

    for gtfs_file in gtfs_files_sorted:
        feed = gtfs_service.load_gtfs_feed_from_redis(gtfs_file)

        if not feed:
            continue

        # Extract dataframes from GTFS feed
        calendar_df = feed.calendar
        trips_df = feed.trips
        stop_times_df = feed.stop_times
        stops_df = feed.stops
        calendar_dates_df = feed.calendar_dates
        
        today_date = datetime.today().date()

        # Check excpetion from calendar_dates
        if calendar_dates_df is not None and not calendar_dates_df.empty:
            date_exceptions = calendar_dates_df[calendar_dates_df['date'] == today_date]

            # Check for exceptions
            active_exceptions = date_exceptions[date_exceptions['exception_type'] == 1]
            deactivated_exceptions = date_exceptions[date_exceptions['exception_type'] == 2]
        else:
            active_exceptions = pd.DataFrame()
            deactivated_exceptions = pd.DataFrame()

        if day_dataframes[current_day_of_week] is None:
            
            '''
              Even though, calendar_dates is inactive in documenation, I received data from ZTM Poznań where they used it. Therefore, I wrote code to handle this situation
            '''

            # Filter active services based on the current day
            active_services = calendar_df[calendar_df[current_day_of_week] == 1]

            # Activate exceptions to active service_id
            if not active_exceptions.empty:
                active_services = pd.concat([
                    active_services,
                    active_exceptions.merge(calendar_df, on='service_id', how='left')
                ]).drop_duplicates('service_id')

            # Delete deactivated service_id
            if not deactivated_exceptions.empty:
                active_services = active_services[~active_services['service_id'].isin(deactivated_exceptions['service_id'])]

            if not active_services.empty:

                # Merge dataframes to get the full schedule
                trips_on_day = pd.merge(active_services, trips_df, on='service_id')
                stop_times_on_day = pd.merge(trips_on_day, stop_times_df, on='trip_id')
                full_schedule = pd.merge(stop_times_on_day, stops_df, on='stop_id')

                # Filter schedule based on the given variables
                full_schedule_filtered = full_schedule[
                    (full_schedule['stop_id'] == stop_id) & 
                    (full_schedule['route_id'] == route_id) &
                    (full_schedule['direction_id'] == direction_id)
                ]
                day_dataframes[current_day_of_week] = full_schedule_filtered
                

        if day_dataframes[current_day_of_week] is not None:
            break

    if day_dataframes[current_day_of_week] is not None:
        # Prepare final dataframe for the response
        final_df = day_dataframes[current_day_of_week][['route_id', 'departure_time', 'start_date', 'stop_id', 'direction_id', 'trip_id', 'stop_headsign', 'stop_name']].sort_values(by='departure_time')

        # Regex function and removec seconds
        final_df['departure_time'] = final_df['departure_time'].apply(convert_time).str.slice(0, 5)
        stop_headsign = final_df['stop_headsign'].iloc[0]
        stop_name = final_df['stop_name'].iloc[0]


        current_day_info = {
            'current_day': current_day_of_week,
            'schedules' : final_df.to_dict(orient='records'),
            'stop_name': stop_name,
            'stop_headsign': stop_headsign
        }
        response_data = current_day_info
        return response_data


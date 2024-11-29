import tempfile
import os
import re
import gtfs_kit as gk
import redis
import pandas as pd
from datetime import datetime

class GTFSService:
    def __init__(self, route_id, stop_id, direction_id, current_day_of_week):
        self.route_id = route_id
        self.stop_id = stop_id
        self.direction_id = direction_id
        self.current_day_of_week = current_day_of_week
        self.client = redis.StrictRedis(host='redis', port=6379, db=0)

    def fetch_gtfs_files_from_redis(self):
        try:
            # Fetches all keys from Redis, filters out keys ending with ':hash', decodes them to strings, and returns the list of remaining keys.
            all_keys = self.client.keys('*')
            gtfs_keys = []
            
            for key in all_keys:
                decoded_key = key.decode('utf-8')
                
                if not decoded_key.endswith(':hash'):
                    gtfs_keys.append(decoded_key)

            return gtfs_keys
        
        except Exception as e:
            return {'error': 'There was an error ' + str(e)}
        
    def load_gtfs_feed_from_redis(self,filename):
        try:
            file_content = self.client.get(filename)
            if file_content:

                # Use a temporary file to handle the GTFS data
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

    def extract_date_from_filename(self, filename):
        try:

            # Extract date from the filename (e.g., '20240907_20240930.zip')
            date_str = filename.split('_')[0]

            # Convert string to date object
            return datetime.strptime(date_str, '%Y%m%d')
        except ValueError:

            # If the date format is invalid, skip this file
            return None    
        
    def convert_time(self, departure_time):
        pattern = re.compile(r"(2[4-9]):([0-5][0-9])")
        match = pattern.match(departure_time)
        if match:
            hour = int(match.group(1))
            new_hour = hour - 24
            return f"{new_hour}:{match.group(2)}"
        
        return departure_time

    def get_schedule(self):
        gtfs_files = self.fetch_gtfs_files_from_redis()
        if not gtfs_files:
            return None
        
        # Filter and sort GTFS files based on date extracted from filename
        gtfs_files_filtered = []
        for file in gtfs_files:
            date = self.extract_date_from_filename(file)
            if date is not None:
                gtfs_files_filtered.append(file)
        gtfs_files_sorted = sorted(gtfs_files_filtered, key=self.extract_date_from_filename, reverse=True)

        day_dataframes = {}

        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            day_dataframes[day] = None

        for gtfs_file in gtfs_files_sorted:
            feed = self.load_gtfs_feed_from_redis(gtfs_file)
            if not feed:
                continue

            # Extract dataframes from GTFS feed
            calendar_df = feed.calendar
            trips_df = feed.trips
            stop_times_df = feed.stop_times
            stops_df = feed.stops
            calendar_dates_df = feed.calendar_dates
            
            today_date = datetime.today().date()
            active_services = self.get_active_services(calendar_df, calendar_dates_df, today_date)

            if day_dataframes[self.current_day_of_week] is None:
                day_dataframes[self.current_day_of_week] = self.process_schedule(active_services, trips_df, stop_times_df, stops_df)

        if day_dataframes[self.current_day_of_week] is not None:
            return self.format_schedule(day_dataframes[self.current_day_of_week])
        return None

    def get_active_services(self, calendar_df, calendar_dates_df, today_date):
        if calendar_dates_df is not None and not calendar_dates_df.empty:
            date_exceptions = calendar_dates_df[calendar_dates_df['date'] == today_date]
            active_exceptions = date_exceptions[date_exceptions['exception_type'] == 1]
            deactivated_exceptions = date_exceptions[date_exceptions['exception_type'] == 2]
        else:
            active_exceptions = pd.DataFrame()
            deactivated_exceptions = pd.DataFrame()

        active_services = calendar_df[calendar_df[self.current_day_of_week] == 1]

        if not active_exceptions.empty:
            active_services = pd.concat([active_services, active_exceptions.merge(calendar_df, on='service_id', how='left')]).drop_duplicates('service_id')

        if not deactivated_exceptions.empty:
            active_services = active_services[~active_services['service_id'].isin(deactivated_exceptions['service_id'])]

        return active_services

    def process_schedule(self, active_services, trips_df, stop_times_df, stops_df):
        trips_on_day = pd.merge(active_services, trips_df, on='service_id')
        stop_times_on_day = pd.merge(trips_on_day, stop_times_df, on='trip_id')
        full_schedule = pd.merge(stop_times_on_day, stops_df, on='stop_id')
        filtered_schedule = full_schedule[
            (full_schedule['stop_id'] == self.stop_id) &
            (full_schedule['route_id'] == self.route_id) &
            (full_schedule['direction_id'] == self.direction_id)
        ]
        return filtered_schedule.sort_values(by='departure_time')

    def format_schedule(self, schedule_df):
        schedule_df['departure_time'] = schedule_df['departure_time'].apply(self.convert_time).str.slice(0, 5)
        stop_headsign = schedule_df['stop_headsign'].iloc[0]
        stop_name = schedule_df['stop_name'].iloc[0]

        return {
            'current_day': self.current_day_of_week,
            'schedules': schedule_df[['route_id', 'departure_time', 'start_date', 'stop_id', 'direction_id', 'trip_id', 'stop_headsign', 'stop_name']].sort_values(by='departure_time').to_dict(orient='records'),
            'stop_name': stop_name,
            'stop_headsign': stop_headsign
        }

    def get_trip_details(self):

        # --> trips.txt contain route_id and trips_id --> 

        # -- > stop_times.txt contain trip ID and stops_id in order(stop_sequence) -->
        
        # --> stops.txt contain stops_id and stops_name

        # Getting data from redis

        pass
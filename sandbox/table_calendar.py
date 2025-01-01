 # Create a dataframe for each dat of the week separately, and script that will extract 1 from calendar.txt and populate data accordingly, if any data is already avalible, skip it. If a date i closer to current day, do nothing.
#            Monday                                               
# +------------------------------------------+
# |          from file calendar.txt          |
#              1                             |
# |        service_id = x                    |

import gtfs_kit as gk
import pandas as pd
from datetime import datetime

# Simple function to load GTFS feed from a zip file
def load_gtfs_feed(path_to_gtfs):
    return gk.feed.read_feed(path_or_url=path_to_gtfs, dist_units='km')

# Function to extract the date from the filename
def extract_date_from_filename(filename):
    # Example: from '20240907_20240930.zip' we extract '20240907'
    date_str = filename.split('_')[0]
    # Convert the string to a date object
    return datetime.strptime(date_str, '%Y%m%d')

# List of GTFS files
gtfs_files = ['20240828_20240830.zip', '20240827_20240831.zip', '20240907_20240930.zip', '20241105_20241130.zip']

# Sort files by the extracted date, from newest to oldest
gtfs_files_sorted = sorted(gtfs_files, key=extract_date_from_filename, reverse=True)

# List of days of the week
days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

# Create a dictionary to store data for each day of the week
day_dataframes = {day: None for day in days_of_week}

# Check what the current day of the week is
# current_day_of_week = days_of_week[datetime.today().weekday()]
current_day_of_week = 'monday'

# Loop through GTFS files from newest to oldest
for gtfs_file in gtfs_files_sorted:
    # Load data from the GTFS file
    feed = load_gtfs_feed(gtfs_file)

    # Load necessary tables from the feed
    calendar_df = feed.calendar
    trips_df = feed.trips
    stop_times_df = feed.stop_times
    stops_df = feed.stops
    calendar_dates_df = feed.calendar_dates

    
    today_date = datetime.today().date()
    # today_date = datetime(2024, 11, 18).date()
    
    # Check excpetion from calendar_dates
    # date_exceptions = calendar_dates_df[calendar_dates_df['date'] == today_date]

    # Check if we already have data for the current day of the week
    if day_dataframes[current_day_of_week] is None:
        # Look for active services for the current day of the week
        active_services = calendar_df[calendar_df[current_day_of_week] == 1]

        # active_exceptions = date_exceptions[date_exceptions['exception_type'] == 1]
        # deactivated_exceptions = date_exceptions[date_exceptions['exception_type'] == 2]

        # active_services = pd.concat([
        #     active_services,
        #     active_exceptions.merge(calendar_df, on='service_id', how='left')
        # ]).drop_duplicates('service_id')

        # active_services = active_services[~active_services['service_id'].isin(deactivated_exceptions['service_id'])]

        # If active services exist
        if not active_services.empty:
            # Merge service data with trip data
            trips_on_day = pd.merge(active_services, trips_df, on='service_id')
            # Merge trip data with stop times
            stop_times_on_day = pd.merge(trips_on_day, stop_times_df, on='trip_id')
            # Merge with stop names
            full_schedule = pd.merge(stop_times_on_day, stops_df, on='stop_id')

            # Filter by stop_id and route_id
            full_schedule_filtered = full_schedule[
                (full_schedule['stop_id'] == '1204') & 
                (full_schedule['route_id'] == '388')
            ]

            # Save the result for the current day of the week
            day_dataframes[current_day_of_week] = full_schedule_filtered

    # Stop searching if data for the current day is found
    if day_dataframes[current_day_of_week] is not None:
        break

# Display the schedule for the current day
if day_dataframes[current_day_of_week] is not None:
    print(f"Schedule for {current_day_of_week.capitalize()}:")
    # Sort by departure time
    print(day_dataframes[current_day_of_week][['route_id', 'departure_time', 'stop_name', 'start_date']].sort_values(by='departure_time'))
else:
    print(f"No schedule found for {current_day_of_week.capitalize()}.")




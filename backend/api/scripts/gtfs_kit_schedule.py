import gtfs_kit as gk
import pandas as pd


# # Path to the GTFS zip file
path_to_gtfs = '20240907_20240930.zip'

# # Load the GTFS data
feed = gk.feed.read_feed(path_or_url=path_to_gtfs, dist_units='km')

# Wczytywanie plików GTFS
calendar_df = feed.calendar
trips_df = feed.trips
stop_times_df = feed.stop_times
stops_df = feed.stops

# Filtered services by day of the week 
monday_services = calendar_df[calendar_df['monday'] == 1]

# Merge trips_txt based on service_id
trips_on_monday = pd.merge(monday_services, trips_df, on='service_id')

# Merge stops_times.txt based on trip_id
stop_times_on_monday = pd.merge(trips_on_monday, stop_times_df, on='trip_id')

# Merge stops.txt based on stop_id 
full_schedule = pd.merge(stop_times_on_monday, stops_df, on='stop_id')

# Filtered by route_id
filtered_by_route = full_schedule[full_schedule['route_id'] == '16']

# Filtered in filtered schedule by stop_id
filtered_schedule = filtered_by_route[filtered_by_route['stop_id'] == '214']

# Select relevant columns for presentation
columns_to_show = ['route_id', 'departure_time', 'stop_name']
final_df = filtered_schedule[columns_to_show]

# Sort by departure_time in ascending order
final_df_sorted = final_df.sort_values(by='departure_time')

print(final_df_sorted)


'''
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

                                                                Weeks
-------------------------------------------------------------------------------------------------------------
           Monday                                               
+------------------------------------------+
|           from file calendar.txt         |
|             1                            |
|        service_id = x                    |
|  +------------------------------------+  |
|  | from file trips.txt                |  |
|  |   service_id = x                   |  |
|  |   route_id                         |  |
|  |  trip_id = y                       |  |
|  |  +-----------------------------+   |  |
|  |  | from file stop_times.txt    |   |  | 
|  |  |    trip_id = y              |   |  |
|  |  |    departure_time           |   |  |
|  |  |    stop_id = z              |   |  |
|  |  |  +----------------------+   |   |  |
|  |  |  | from file stops.txt  |   |   |  |
|  |  |  |      stop_id = z     |   |   |  |
|  |  |  |      stop_name       |   |   |  |
|  |  |  |                      |   |   |  |
|  |  |  |                      |   |   |  |
|  |  |  |                      |   |   |  |
|  |  |  |                      |   |   |  |
|  |  |  +----------------------+   |   |  |
|  |  |                             |   |  |
|  |  +-----------------------------+   |  |
|  |                                    |  |
|  +------------------------------------+  |
|                                          |
+------------------------------------------+



'''
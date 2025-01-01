import gtfs_kit as gk
import pandas as pd
import redis
import json

client = redis.Redis(host='172.19.0.2')
DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

path_to_gtfs = '20240907_20240930.zip'
feed = gk.feed.read_feed(path_or_url=path_to_gtfs, dist_units='km')

calendar_df = feed.calendar
trips_df = feed.trips
stop_times_df = feed.stop_times
stops_df = feed.stops

# for day in DAYS_OF_WEEK:
#     day_services = calendar_df[calendar_df[day] == 1]

#     trips_on_day = pd.merge(day_services, trips_df, on='service_id')

#     stop_times_on_day = pd.merge(trips_on_day, stop_times_df, on='trip_id')
#     print(stop_times_on_day.columns)

#     full_schedule = pd.merge(stop_times_on_day, stops_df, on='stop_id')
#     print(full_schedule.columns)

#     full_schedule_json = full_schedule.to_json(orient='records')

#     # Saving to redis
#     client.set(f"full_schedule_{day}", full_schedule_json)
#     print(f"Saving full_schedule_{day}")


# --------------------------------------- ODCZYT ------------------------------------

retrieved_data = client.get("full_schedule_friday")

retrieved_data_str = retrieved_data.decode('utf-8')
retrieved_data_str = retrieved_data_str.replace('\\"', '"')
retrieved_json = json.loads(retrieved_data_str)

retrieved_df = pd.DataFrame(retrieved_json)


route_id = '16'
stop_id = '214'
direction_id ='0'

# Filtracja po route_id i stop_id
# filtered_by_route = retrieved_df[retrieved_df['route_id'] == route_id]
# filtered_schedule = filtered_by_route[filtered_by_route['stop_id'] == stop_id]
direction_id = int(direction_id)

full_schedule_filtered = retrieved_df[
    (retrieved_df['route_id'] == route_id) & 
    (retrieved_df['stop_id'] == stop_id) & 
    (retrieved_df['direction_id'] == direction_id)
]

columns_to_show = ['route_id', 'departure_time', 'stop_name', 'direction_id']
final_df = full_schedule_filtered[columns_to_show]

final_df_sorted = final_df.sort_values(by='departure_time')

print(final_df_sorted)
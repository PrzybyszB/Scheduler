from collections import Counter

def convert_txt_to_json(txt_content):
    lines = txt_content.splitlines()
    header = lines[0].split(",")  
    json_data = []

    for line in lines[1:]:
        values = line.split(",")
        json_data.append(dict(zip(header, values)))

    return json_data

    # stop_times.txt contain trip ID and stops_id in order(stop_sequence) and last stop(stop_headsign)
    
    # --> trips.txt with Trip ID contain route_id --> route_id

with open('stop_times.txt', 'r', encoding='utf-8-sig') as file:
    stop_times_data = file.read()

with open('trips.txt', 'r', encoding='utf-8-sig') as file:
    trips_data = file.read()

with open('stops.txt', 'r', encoding='utf-8-sig') as file:
    stops_data = file.read()

# with open('GTFS-ZTM/GTFS-ZTM-STATIC/stop_times.txt', 'r', encoding='utf-8-sig') as file:
#     stop_times_data = file.read()
# with open('GTFS-ZTM/GTFS-ZTM-STATIC/trips.txt', 'r', encoding='utf-8-sig') as file:
#     trips_data = file.read()
# with open('GTFS-ZTM/GTFS-ZTM-STATIC/stops.txt', 'r', encoding='utf-8-sig') as file:
#     stops_data = file.read()
    

stop_times_json_data = convert_txt_to_json(stop_times_data)
trips_json_data = convert_txt_to_json(trips_data)
stops_json_data = convert_txt_to_json(stops_data)


routes = {}


route_id ="16"

# Itereting data from trips.txt to get trip_id
for trips in trips_json_data:
    trips_route_id = trips['route_id']
    if trips_route_id == route_id:
        trip_id = trips['trip_id']
        routes[trip_id]= []
        
# Itereting data from stop_times.txt to get departure time and trip_id
for stop_times in stop_times_json_data:
    stop_times_trip_id = stop_times['trip_id']
    stop_times_stop_id = stop_times['stop_id']
    departure_time = stop_times['departure_time']
    
    # Check that stop_times_trip_id is the same like in trip_id in routes
    if stop_times_trip_id in routes:

        # Adding dict with indetity stop_id and departure_time
        routes[stop_times_trip_id].append({
            'stop_id': stop_times_stop_id,
            'departure_time': departure_time
        })

# Make dict with stops
stops_dict = {}
for stops in stops_json_data:
    stop_id = stops['stop_id']
    stop_name = stops['stop_name']
    stops_dict[stop_id] = stop_name

# Changing routes to get stops_name instead of stops_id
for trip_id, stop_details in routes.items():
    stop_names = []
    for detail in stop_details:
        stop_id = detail['stop_id']
        departure_time = detail['departure_time']
        stop_name = stops_dict.get(stop_id, None)
        if stop_name:
            stop_names.append({
                'stop_id': stop_id,
                'stop_name': stop_name,
                'departure_time': departure_time
                })
        # else:
        #     print(f"Warning: Stop ID {stop_id} not found in stops_dict")
    routes[trip_id] = stop_names


# Itereting departure time on stops for trip id 
for trip_id, stop_details in routes.items():
    print(f"Route_id: {route_id} Trip ID: {trip_id}")
    for detail in stop_details:
        stop_name = detail['stop_name']
        departure_time = detail['departure_time']
        stop_id = detail['stop_id']
        print(f" {stop_id} Stop name: {stop_name}, Departure Time: {departure_time}")
    print()

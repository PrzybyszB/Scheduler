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


route_id ="3"

# Itereting data from trips.txt to get trip_id
for trips in trips_json_data:
    trips_route_id = trips['route_id']
    direction_id = trips['direction_id']
    if trips_route_id == route_id:
        trip_id = trips['trip_id']
        routes[trip_id] = {
            'direction_id' : direction_id,
            'stop_details': []}

# Itereting data from stop_times.txt to get departure time and trip_id
for stop_times in stop_times_json_data:
    stop_times_trip_id = stop_times['trip_id']
    stop_times_stop_id = stop_times['stop_id']
    departure_time = stop_times['departure_time']
    
    # Check that stop_times_trip_id is the same like in trip_id in routes
    if stop_times_trip_id in routes:
        
        # Adding dict with indetity stop_id and departure_time
        routes[stop_times_trip_id]['stop_details'].append({
            'stop_id': stop_times_stop_id,
            'departure_time': departure_time
        })
# print(routes)
# Make dict with stops
stops_dict = {}
for stops in stops_json_data:
    stop_id = stops['stop_id']
    stop_name = stops['stop_name']
    stops_dict[stop_id] = stop_name

# Changing routes to get stops_name instead of stops_id
for trip_id, trip_info in routes.items():
    stop_names = []
    for detail in trip_info['stop_details']:
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
    routes[trip_id]['stop_details'] = stop_names


# Itereting departure time on stops for trip id 
# for trip_id, stop_details in routes.items():
#     direction_id = trip_info['direction_id']
#     print(f"Trip ID: {trip_id}, Direction ID: {direction_id}")
#     for detail in stop_details:
#         stop_name = detail['stop_name']
#         departure_time = detail['departure_time']
#         print(f"  Stop name: {stop_name}, Departure Time: {departure_time}")
#     print()

# ------------------------------------------------------------ ROUTES PATTERN -----------------------------------------

# print("Routes structure:")
# for trip_id, stop_details in routes.items():
#     print(f"Trip ID: {trip_id}")
#     for detail in stop_details:
#         print(f" Stop ID: {detail.get('stop_id')}, Departure Time: {detail.get('departure_time')}")


def get_stop_sequences(routes):
    sequences = []
    
    for trip_id, trip_info in routes.items():
        # trip_id = stops['trip_id']
        sequence =[]
        # Making sequences stops_ids of list in order
        for stop in trip_info['stop_details']:
            stop_id = stop['stop_id']
            stop_name = stop['stop_name']
            sequence.append(stop_name)
        direction_id = trip_info['direction_id']
        sequences.append((tuple(sequence), direction_id))

        # print(f"Trip ID: {trip_id}, Stops: {sequence}")
    
    return sequences

def find_common_patterns(sequences, min_occurrences=10):
    sequence_counter = Counter(sequences)
    common_patterns = {}

    for pattern, count in sequence_counter.items():
        if count >= min_occurrences:
            common_patterns[pattern] = count
    
    return common_patterns




sequences = get_stop_sequences(routes)

# Finding patterns
common_patterns = find_common_patterns(sequences)


for (pattern, direction_id), count in common_patterns.items():
    print(f"Pattern: {pattern}, Direction ID: {direction_id}, Count: {count}")
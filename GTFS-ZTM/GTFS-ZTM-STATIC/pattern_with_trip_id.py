
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
        trip_headsign = trips['trip_headsign']
        routes[trip_id]= {
            'headsign' : trip_headsign,
            'stops' : []
        }
        
# Itereting data from stop_times.txt to get departure time and trip_id
for stop_times in stop_times_json_data:
    stop_times_trip_id = stop_times['trip_id']
    stop_times_stop_id = stop_times['stop_id']
    departure_time = stop_times['departure_time']
    
    
    # Check that stop_times_trip_id is the same like in trip_id in routes
    if stop_times_trip_id in routes:

        # Adding dict with indetity stop_id and departure_time
        routes[stop_times_trip_id]['stops'].append({
            'stop_id': stop_times_stop_id,
            'departure_time': departure_time,
            
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
    for detail in stop_details['stops']:
        stop_id = detail['stop_id']
        departure_time = detail['departure_time']
        stop_name = stops_dict.get(stop_id, None)
        if stop_name:
            stop_names.append({
                'stop_id': stop_id,
                'stop_name': stop_name,
                'departure_time': departure_time,
                })
        # else:
        #     print(f"Warning: Stop ID {stop_id} not found in stops_dict")
    routes[trip_id] = stop_names


# Itereting departure time on stops for trip id 
# for trip_id, stop_details in routes.items():
#     print(f"Trip ID: {trip_id}")
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
    sequences = {}
    
    for trip_id, stops in routes.items():
        stop_ids = []
        stop_names = []

        for stop in stops:
            stop_id = stop['stop_id']
            stop_name = stop['stop_name']
            stop_ids.append(stop_id)
            stop_names.append(stop_name)
        
        # Making a tuple to get IDS(stop_ids) for sequence
        sequence = tuple(stop_ids)

        if sequence not in sequences:
            sequences[sequence] = {
                "trip_ids": [],
                "stops": [],
            }
        sequences[sequence]["trip_ids"].append(trip_id)
        

# >>> for i,v in enumerate(["xd","xdd"]):
# ...     print(f"index: {i} value: {v}")
# ... 
# index: 0 value: xd
# index: 1 value: xdd


        stop_descriptions = []
        for i in range(len(stop_ids)):
            stop_id = stop_ids[i]
            stop_name = stop_names[i]
            stop_descriptions.append((stop_id, stop_name))
        

        sorted_stops = []
        for stop_id in stop_ids:
            for stop in stop_descriptions:
                if stop[0] == stop_id:
                    sorted_stops.append(f'{stop[0]} = {stop[1]}')
        
        sequences[sequence]["stops"] = sorted_stops
    
    return sequences


def find_common_patterns(sequences):
    items = list(sequences.items())
    patterns_counter = []
    index = 1

    for pattern, data in items:
        stops_display = ", ".join(data['stops'])
        trip_ids_display = ", ".join(data['trip_ids'])
        
        
        counter = len(data['trip_ids'])
        patterns_counter.append(counter)


        print(f"Pattern {index}: ({stops_display})")
        print(f"Counter: {counter}")
        print(f"Trip_ids  = ({trip_ids_display})\n")
        

        index += 1
    
    two_most_common_pattern = sorted(patterns_counter, reverse=True)[:2]

    print(f"Two most common patterns: {two_most_common_pattern}")




sequences = get_stop_sequences(routes)

# Finding patterns and trip_ids
common_patterns = find_common_patterns(sequences)


def convert_txt_to_json(txt_content):
    lines = txt_content.splitlines()
    header = lines[0].split(",")
    json_data = []

    fail_line = []
    for line in lines[1:]:
        values = line.split(",")
        fail_line.append(values)
        if len(values) != len(header):
            # Handling unexpected number of values
            # print(f"Skipping line with unexpected number of values: {line}")
            # print(len(fail_line))
            continue
        
        # Handling special characters or formatting issues
        values = [value.strip().strip('"') for value in values]

        # Append data to JSON
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


route_id = "16"

# Itereting data from trips.txt to get trip_id
for trips in trips_json_data:
    trips_route_id = trips['route_id']
    if trips_route_id == route_id:
        trip_id = trips['trip_id']
        trip_headsign = trips['trip_headsign']
        routes[trip_id]= {
            'headsign' : trip_headsign,
            'stops_detail' : []
        }
        
# Itereting data from stop_times.txt to get departure time and trip_id
for stop_times in stop_times_json_data:
    stop_times_trip_id = stop_times['trip_id']
    stop_times_stop_id = stop_times['stop_id']
    departure_time = stop_times['departure_time']
    stop_sequence = stop_times['stop_sequence']
    
    
    # Check that stop_times_trip_id is the same like in trip_id in routes
    if stop_times_trip_id in routes:

        # Adding dict with indetity stop_id and departure_time
        routes[stop_times_trip_id]['stops_detail'].append({
            'stop_id': stop_times_stop_id,
            'departure_time': departure_time,
            'stop_sequence': stop_sequence
        })

# Make dict with stops
stops_dict = {}
for stops in stops_json_data:
    stop_id = stops['stop_id']
    stop_name = stops['stop_name']
    stops_dict[stop_id] = stop_name

# Changing routes to get stops_name instead of stops_id
for trip_id, trip_info in routes.items():
    stop_names = []
    for detail in trip_info['stops_detail']:
        stop_id = detail['stop_id']
        departure_time = detail['departure_time']
        stop_sequence = detail['stop_sequence']
        stop_name = stops_dict.get(stop_id, None)
        if stop_name:
            stop_names.append({
                'stop_name': stop_name,
                'departure_time': departure_time,
                'stop_sequence': stop_sequence
                })
        # else:
        #     print(f"Warning: Stop ID {stop_id} not found in stops_dict")
    routes[trip_id] = {
        'headsign': trip_info['headsign'],
        'stops_detail': stop_names
    }


# Itereting departure time on stops for trip id 
# for trip_id, stop_details in routes.items():
#     print(f"Trip ID: {trip_id}")
#     for detail in stop_details['stops_detail']:
#         stop_name = detail['stop_name']
#         departure_time = detail['departure_time']
#         stop_sequence = detail['stop_sequence']
#         print(f"  Stop name: {stop_name}, Departure Time: {departure_time}, Stop Sequence {stop_sequence}")
#     print()

# ------------------------------------------------------------ ROUTES PATTERN -----------------------------------------

# print("Routes structure:")
# for trip_id, stop_details in routes.items():
#     print(f"Trip ID: {trip_id}")
#     for detail in stop_details:
#         print(f" Stop ID: {detail.get('stop_id')}, Departure Time: {detail.get('departure_time')}")


def get_stop_sequences(routes):
    sequences = {}
    
    for trip_id, trip_data in routes.items():

        headsign = trip_data['headsign']
        stop_names = []

        for stop in trip_data['stops_detail']:
            stop_name = stop['stop_name']
            stop_names.append(stop_name)
        
        # Making a tuple to get IDS(stop_ids) for sequence
        sequence = tuple(stop_names)

        if sequence not in sequences:
            sequences[sequence] = {
                "trip_ids": [],
                "headsign": headsign,
                "stops_details": []
                }   
        sequences[sequence]["trip_ids"].append(trip_id)

        stop_descriptions = []
        for stop in stop_names:
            stop_descriptions.append(stop)
        sequences[sequence]["stops"] = stop_descriptions
    

    return sequences


def find_common_patterns(sequences):
    items = list(sequences.items())
    patterns_result = []
    index = 1
    stops_display = []

    for pattern, data in items:
        stops = data['stops']
        stops_display.append(stops)
        counter = len(data['trip_ids'])


        pattern_info = {
            'stops_display': stops_display,
            'counter': counter,
        }

        patterns_result.append(pattern_info)

        index += 1

    patterns_result.sort(key=lambda x: x['counter'], reverse=True)
    most_common_patterns = patterns_result[:2]

    
    return most_common_patterns


sequences = get_stop_sequences(routes)
common_patterns = find_common_patterns(sequences)

for pattern in common_patterns:
    stops_display = pattern.get('stops_display')  


print(stops_display[1])
print(stops_display[0])


# for pattern in common_patterns:
#     print(f"Pattern {pattern['pattern_index']}: ({pattern['stops_display']})")
    # print(f"HeadSign: {pattern['trip_headsign']}")
    # print(f"Counter: {pattern['counter']}")
    # print(f"Trip_ids = ({pattern['trip_ids_display']})\n")




from api.tasks import client
import csv
from io import StringIO


def fetch_data_from_redis(keys):
    '''
    Fetch data from redis and decode it 
    '''
    fetch_data = {}
    try:
        for key in keys:
            data = client.get(key).decode('utf-8')
            fetch_data[key] = data
        return fetch_data
    except (ConnectionError, TimeoutError) as e:
        raise Exception(f"Error retrieving data from Redis: {e}")

def parse_csv_data(data):
    '''
    Parse CSV data into Dict Reader obejcts
    '''
    csv_data = {}

    for key, value in data.items():
        csv_data[key] = csv.DictReader(StringIO(value))
    return csv_data

def process_trips(trips_csv, route_id):
    '''
    Process trips to filter by route_id and generate a dict of routes
    '''

    routes = {}
    # Itereting data from trips.txt to get trip_id
    for trips in trips_csv:
        trips_route_id = trips['route_id']
        direction_id = trips['direction_id']
        if trips_route_id == route_id:
            trip_id = trips['trip_id']
            routes[trip_id] ={
                'direction_id': direction_id,
                'stops_detail': []
            }
    return routes

def process_stop_times(stop_times_csv, routes):
    '''
    Add stop times to routes based on trip_id
    '''
    for stop_time in stop_times_csv:
        trip_id = stop_time['trip_id']
        stop_id = stop_time['stop_id']

        # Check that stop_times_trip_id is the same like in trip_id in routes
        if trip_id in routes:
            routes[trip_id]['stops_detail'].append({
                'stop_id': stop_id,
            })
    
    return routes

def create_stops_dict(stops_csv):
    '''
    Create a dict mapping stop_id to stop_name
    '''

    stops_dict = {}

    for stops in stops_csv:
        stop_id = stops['stop_id']
        stop_name = stops['stop_name']
        stops_dict[stop_id] = stop_name

    return stops_dict

def map_stop_names_to_routes(routes, stops_dict):
    '''
    Map stop names to routes
    '''
    for trip_id, trip_info in routes.items():
        stop_names = []
        for detail in trip_info['stops_detail']:
            stop_id = detail['stop_id']
            if stop_id in stops_dict: 
                stop_name = stops_dict[stop_id]
                stop_names.append({
                    'stop_name': stop_name,
                    'stop_id': stop_id
                })
        routes[trip_id]['stops_detail'] = stop_names

def identify_popular_patterns(routes):
    '''
    Identify the most popular patterns for each direction_id
    '''
    sequences = {}    
    for trip_id, trip_data in routes.items():
        stop_names = trip_data['stops_detail']
            
        # Getting the direction_id from the routes
        direction_id = trip_data['direction_id']
            
        # Making a list with stops name 
        stop_ids = []
        for stop in stop_names:
            stop_ids.append(stop['stop_id'])

        # Making a tuple to get IDS(stop_ids) for sequence
        sequence = tuple(stop_ids)

        if sequence not in sequences:
            sequences[sequence] = {
                'direction_id': direction_id,  # Ensure this key exists
                'trip_ids': [],
                'stops': stop_names,
            }
        sequences[sequence]["trip_ids"].append(trip_id)

    patterns = {}
    for sequence, data in sequences.items():
        direction_id = data['direction_id']
        count = len(data['trip_ids'])

        # Add patterns that get more than 2 reapets
        if count > 1:
            if direction_id not in patterns:
                patterns[direction_id] = {
                    'stops': data['stops'],
                    'count': count
                }
            else:
                # Check that the pattren is the most popular
                if count > patterns[direction_id]['count']:
                    patterns[direction_id] = {
                        'stops': data['stops'],
                        'count': count
                    }
    return patterns

def get_trip_detail(route_id):
    '''
     ---> trips.txt contain route_id and trips_id --->
     ---> stop_times.txt contain trip_id and stops_id in order(stop_sequence) --->
     ---> stops.txt contain stops_id and stops_name
    '''

    try:
        # Get data from redis
        keys = ['stop_times.txt', 'trips.txt', 'stops.txt']
        raw_data = fetch_data_from_redis(keys)

        # Parse data to csv
        csv_data = parse_csv_data(raw_data)

        # Process data
        routes = process_trips(csv_data['trips.txt'], route_id)
        process_stop_times(csv_data['stop_times.txt'], routes)
        stops_dict = create_stops_dict(csv_data['stops.txt'])
        map_stop_names_to_routes(routes, stops_dict)

        # Find popular patterns
        patterns = identify_popular_patterns(routes)

        
        response_data = { 
            "route id": route_id,
            "most_popular_patterns": {}
        }
        for direction_id, pattern in patterns.items():
            response_data["most_popular_patterns"][direction_id] = {
                'stops': pattern['stops'],
            }

        return response_data
    except Exception as e:
        return {"error": str(e)}

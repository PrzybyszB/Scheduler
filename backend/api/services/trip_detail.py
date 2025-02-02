import json
from .gtfs_processing import GTFSService
from .stop_detail import create_stops_dict

gtfs_service = GTFSService()

def process_trips(trips_csv, route_id):
    '''
    Process trips to filter by route_id and generate a dict of routes
    '''
    routes = {}
    # Itereting data from trips.txt to get trip_id
    for trips in trips_csv:
        trips_route_id = trips['route_id']
        direction_id = trips['direction_id']
        trip_headsign = trips['trip_headsign']
        if trips_route_id == route_id:
            trip_id = trips['trip_id']
            routes[trip_id] ={
                'direction_id': direction_id,
                'trip_headsign': trip_headsign,
                'stops_detail': []
            }
    return routes

def process_stop_times(stop_times_csv, routes):
    """
    Add stop times to routes based on trip_id.
    """
    for stop_time in stop_times_csv:
        trip_id = stop_time['trip_id']
        stop_id = stop_time['stop_id']
        if trip_id in routes:
            routes[trip_id]['stops_detail'].append({
                'stop_id': stop_id,
            })       
    return routes

def map_stop_names_to_routes(routes, stops_dict):
    '''
    Map stop names to routes and assign trip_headsign
    '''
    for trip_id, trip_info in routes.items():
        stop_names = []
        for detail in trip_info['stops_detail']:
            stop_id = detail['stop_id']
            if stop_id in stops_dict: 
                stop_name = stops_dict[stop_id]['stop_name']
                stop_names.append({
                    'stop_name': stop_name,
                    'stop_id': stop_id
                })
        routes[trip_id]['stops_detail'] = stop_names

        trip_headsign = trip_info['trip_headsign']
        routes[trip_id]['trip_headsign'] = trip_headsign

def identify_popular_patterns(routes):
    '''
    Identify the most popular patterns for each direction_id.
    '''
    sequences = {}    
    for trip_id, trip_data in routes.items():
        stop_names = trip_data['stops_detail']
            
        # Getting the direction_id from the routes
        direction_id = trip_data['direction_id']
        trip_headsign = trip_data['trip_headsign']
            
        # Making a list with stops name 
        stop_ids = []
        for stop in stop_names:
            stop_ids.append(stop['stop_id'])

        # Making a tuple to get IDS(stop_ids) for sequence
        sequence = tuple(stop_ids)

        if sequence not in sequences:
            sequences[sequence] = {
                'direction_id': direction_id,  # Ensure this key exists
                'trip_headsign': trip_headsign,
                'trip_ids': [],
                'stops': stop_names,
            }
        sequences[sequence]["trip_ids"].append(trip_id)

    patterns = {}
    for sequence, data in sequences.items():
        direction_id = data['direction_id']
        trip_headsign = data['trip_headsign']
        count = len(data['trip_ids'])

        # Add patterns that get more than 2 repeats
        if count > 1:
            if direction_id not in patterns:
                patterns[direction_id] = {
                    'stops': data['stops'],
                    'trip_headsign': trip_headsign,
                    'count': count
                }
            else:
                # Check that the pattern is the most popular
                if count > patterns[direction_id]['count']:
                    patterns[direction_id] = {
                        'stops': data['stops'],
                        'trip_headsign': trip_headsign,
                        'count': count
                    }
    return patterns

def fetch_and_save_trip_detail(route_id):
    '''
    Fetch trip details for a given route_id and save to Redis.
    '''
    # Get data from Redis
    keys = ['stop_times.txt', 'trips.txt', 'stops.txt']
    raw_data = gtfs_service.fetch_data_from_redis(keys)
    
    # Parse data to CSV
    csv_data = gtfs_service.parse_csv_data(raw_data)

    routes = process_trips(csv_data['trips.txt'], route_id)

    process_stop_times(csv_data['stop_times.txt'], routes)
    stops_dict = create_stops_dict(csv_data['stops.txt'])
    map_stop_names_to_routes(routes, stops_dict)

    patterns = identify_popular_patterns(routes)

    response_data = { 
        "route id": route_id,
        "most_popular_patterns": {}
    }
    for direction_id, pattern in patterns.items():
        response_data["most_popular_patterns"][direction_id] = {
            'stops': pattern['stops'],
            'trip_headsign': pattern['trip_headsign'],
        }


    redis_key = f"route:{route_id}"

    redis_data = json.dumps(response_data)
    
    # Save data to redis
    gtfs_service.client.hset(redis_key, mapping={'data': redis_data})

    return response_data

def get_trip_detail(route_id):
    '''
    Retrieve trip details for a specific route_id from Redis.
    '''

    redis_key = f"route:{route_id}"
    try:
        route_data = gtfs_service.client.hget(redis_key, 'data')
        if route_data:
            return json.loads(route_data)
        else:
            raise ValueError(f"No data found for route_id {route_id}")
    except Exception as e:
        print(f"Error fetching data for route_id {route_id}: {e}")
        return None

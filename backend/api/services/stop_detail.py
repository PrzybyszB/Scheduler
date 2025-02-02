import pandas as pd
import json
from .gtfs_processing import GTFSService

gtfs_service = GTFSService()

def create_stops_dict(stops_csv):
    """
    Create a dict mapping stop_id to stop_name.
    """
    stops_dict = {}
    for stops in stops_csv:
        stop_id = stops['stop_id']
        stop_name = stops['stop_name']
        stops_dict[stop_id] = {
            'stop_name': stop_name}
    return stops_dict


def get_route_ids_on_stop_for_redis(stop_id):
    """
    Extracting the route_ids of circulating buses for a stop.
    """
    gtfs_files = gtfs_service.fetch_gtfs_files_from_redis()

    if not gtfs_files:
        raise ValueError("No GTFS files available in Redis.")
    
    # Sort and filter GTFS files in one step
    gtfs_files_sorted = sorted(
        (file for file in gtfs_files if gtfs_service.extract_date_from_filename(file) is not None),
        key=gtfs_service.extract_date_from_filename, reverse=True
    )

    for gtfs_file in gtfs_files_sorted:
        feed = gtfs_service.load_gtfs_feed_from_redis(gtfs_file)
        if not feed:
            continue 
        
        stop_times_df = feed.stop_times[['stop_id', 'trip_id']]
        trips_df = feed.trips[['route_id', 'trip_id', 'direction_id']]

        # Filter and join
        merged_df = pd.merge(
            stop_times_df[stop_times_df['stop_id'] == stop_id], 
            trips_df, on='trip_id'
        )

        route_direction_list = merged_df[['route_id', 'direction_id']].drop_duplicates().to_dict(orient='records')

        return {'routes': route_direction_list}

def get_route_ids_for_stop_search(request_get):
    '''
    Fetch route_ids that stop on each stop_id
    '''
    try:
        stop_id = request_get.get('stop_id')

        if not stop_id:
            return {'error': 'stop_id is required'}
        
        redis_key = f"routes_for_stop:{stop_id}"
        routes = gtfs_service.client.get(redis_key)
        decoded_routes = routes.decode('utf-8')

        if not routes:
            raise ValueError(f"No data found for stop_id {stop_id} in Redis")
        
        
        routes_json = json.loads(decoded_routes)

        route_ids = []
        for route in routes_json.get('routes', []):
            route_id = route['route_id']
            direction_id = route['direction_id']
            route_ids.append({'route_id': route_id, 'direction_id': direction_id})
            
        return {'routes': route_ids} 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {'routes': []} 


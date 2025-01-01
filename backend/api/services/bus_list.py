from .gtfs_processing import GTFSService

gtfs_service = GTFSService()

def get_bus_list():
    '''
    Create a list of bus. Their number is between 100-999. 201 and 202 its night tramway.
    '''

    # Fetch active route IDs from Redis
    active_route_ids = gtfs_service.get_active_route_ids()

    if not active_route_ids:
        raise ValueError("No active route IDs found in Redis.")

    bus_ids = []

    for route_id in active_route_ids:
        
        # Decode route_id from bytes to string
        route_id = route_id.decode('utf-8')

        if route_id in {'201', '202'}:
            continue

        if len(route_id) == 3:
            bus_ids.append(route_id)      
        
        response = sorted(set(bus_ids))
    return response
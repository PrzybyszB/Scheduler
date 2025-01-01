import re
from .gtfs_processing import GTFSService

gtfs_service = GTFSService()

def get_tram_list():
    '''
    Create a list of tramway. Their number is between 0-99. The prefix 'T' indicates a replacement for a tram. 201 and 202 its a night tramway
    '''

    # Fetch active route IDs from Redis
    active_route_ids = gtfs_service.get_active_route_ids()

    if not active_route_ids:
        raise ValueError("No active route IDs found in Redis.")

    tram_ids = []

    for route_id in active_route_ids:
        
        # Decode route_id from bytes to string
        route_id = route_id.decode('utf-8')

        if len(route_id) <= 2:
            tram_ids.append(route_id)      

        elif route_id == '201' or route_id == '202':
            tram_ids.append(route_id)
        
        # Regex is for substitute tramway like T2 or T3
        response = sorted(set(tram_ids), key=lambda x: int(re.sub(r'\D', '', x)))

    return response
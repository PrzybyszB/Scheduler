import re
from .gtfs_processing import GTFSService

gtfs_service = GTFSService()

def get_bus_list():
    '''
    Create a list of bus. Their number is between 100-999. 201 and 202 its night tramway.
    '''
    # Fetch GTFS files from Redis
    gtfs_files = gtfs_service.fetch_gtfs_files_from_redis()

    if not gtfs_files:
        raise ValueError("No GTFS files available in Redis.")
    
    # Filter and sort GTFS files based on date extracted from filename
    gtfs_files_filtered = []

    for file in gtfs_files:
        date = gtfs_service.extract_date_from_filename(file)

        if date is not None:
            gtfs_files_filtered.append(file)

    gtfs_files_sorted = sorted(gtfs_files_filtered, key=gtfs_service.extract_date_from_filename, reverse=True)

    bus_ids = []

    for gtfs_file in gtfs_files_sorted:
        feed = gtfs_service.load_gtfs_feed_from_redis(gtfs_file)
        if feed:
            trips_df = feed.trips
            
            df_by_route_id = trips_df[['route_id']].drop_duplicates()

            for index, row in df_by_route_id.iterrows():
                route_id = row['route_id']

                if route_id == '201' or route_id == '202':
                    continue

                elif len(route_id) == 3:
                    bus_ids.append(route_id)      
                
            response = sorted(set(bus_ids))

        return response
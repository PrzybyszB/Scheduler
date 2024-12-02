import re
from .gtfs_processing import GTFSService

gtfs_service = GTFSService()

def get_tram_list():
    '''
    Create a list of tramway. Their number is between 0-99. The prefix 'T' indicates a replacement for a tram. 201 and 202 its a night tramway
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

    tram_ids = []

    for gtfs_file in gtfs_files_sorted:
        feed = gtfs_service.load_gtfs_feed_from_redis(gtfs_file)
        if feed:
            trips_df = feed.trips

            df_by_route_id = trips_df[['route_id']].drop_duplicates()

            for index, row in df_by_route_id.iterrows():
                route_id = row['route_id']

                if len(route_id) <= 2:
                    tram_ids.append(route_id)      

                elif route_id == '201' or route_id == '202':
                    tram_ids.append(route_id)
            
            # Regex is for substitute tramway like T2 or T3
            response = sorted(set(tram_ids), key=lambda x: int(re.sub(r'\D', '', x)))

        return response
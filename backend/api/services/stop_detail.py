import pandas as pd
from .gtfs_processing import GTFSService

gtfs_service = GTFSService()

def get_stop_detail(request_get, queryset):
    """
    Fetches GTFS route and direction data based on the provided stop_id from request.GET.
    """
    stop_id = request_get.get('stop_id')

    if not stop_id:
        return {'error': 'stop_id is required'}

    gtfs_files = gtfs_service.fetch_gtfs_files_from_redis()

    if not gtfs_files:
        raise ValueError("No GTFS files available in Redis.")
    
    gtfs_files_filtered = []
    for file in gtfs_files:
        date = gtfs_service.extract_date_from_filename(file)
        if date is not None:
            gtfs_files_filtered.append(file)

    gtfs_files_sorted = sorted(gtfs_files_filtered, key=gtfs_service.extract_date_from_filename, reverse=True)

    for gtfs_file in gtfs_files_sorted:
        feed = gtfs_service.load_gtfs_feed_from_redis(gtfs_file)
        if feed:
            stop_times_df = feed.stop_times
            trips_df = feed.trips
            
            filtered_by_stops_id = stop_times_df[stop_times_df['stop_id'] == stop_id]
            trip_id_by_stops = pd.merge(filtered_by_stops_id, trips_df, on='trip_id')
            
            final_df = trip_id_by_stops[['route_id', 'direction_id']].drop_duplicates()
            route_direction_list = final_df.to_dict(orient='records')

            return {
                'routes': route_direction_list
            }

    return {'message': 'No valid GTFS files found.'}

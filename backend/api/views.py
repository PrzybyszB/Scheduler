from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Profile, Premium, Route, Stop
from rest_framework import generics, status
from django_filters import rest_framework as filters
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import ProfileSerializer, UserSerializer, PremiumSerializer, RouteSerializer, StopsSerializer
from .tasks import client
from datetime import datetime
# from .services import stop_id, stop_name
import json
import gtfs_kit as gk
import pandas as pd
import csv
from io import StringIO
import os
import tempfile 
import logging
import re
from .services import GTFSService

logger = logging.getLogger('api')

class APIRoot(APIView):
    def get(self, request, format=None):
        return Response({
            'register': '/api/register/',
            'profiles list': '/api/profile/list',
            'profile detail': '/api/profile/user/<int:pk>',
            'user detail': '/api/user/<int:pk>',
            'users list': '/api/user/list',
            'premium create': '/api/premium/create',
            'premium delete': '/api/premium/delete/<int:pk>',
            'premium list': '/api/premium/list',
            'cart': '/api/cart/',
            'transport_detail' : '/api/route/<str:route_id>/', 
            'tram list' : '/api/tram-list',
            'bus list' : '/api/bus-list',
            'stops list' : '/api/stops',
            'schedule for recent day' : '/api/route/<str:route_id>/stop/<str:stop_id>/direction/<str:direction_id>',
            'schedule for request day' : '/api/route/<str:route_id>/stop/<str:stop_id>/direction/<str:direction_id>',
            'search stop' : '/api/stops/?stop_id=<str:stop_id>',

            # Add next endpoints
        })


class CreateUser(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [AllowAny]

class UserProfileList(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    # permission_classes = [IsAuthenticated]

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    # permission_classes = [IsAuthenticated]

class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated]

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated]

class PremiumCreate(generics.CreateAPIView):
    queryset = Premium.objects.all()
    serializer_class = PremiumSerializer
    # permission_classes = [IsAuthenticated]

class PremiumDelete(generics.RetrieveDestroyAPIView):
    queryset = Premium.objects.all()
    serializer_class = PremiumSerializer
    # permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        premium = self.get_object()
        serializer = self.get_serializer(premium)
        premium_data = serializer.data
        premium_id = premium.id
        self.perform_destroy(premium)
        return Response(
            {
                "message": f"Premium with ID {premium_id} was deleted",
                "data": premium_data
            },
            status=status.HTTP_200_OK
        )

class PremiumList(generics.ListAPIView):
    queryset = Premium.objects.all()
    serializer_class = PremiumSerializer
    # permission_classes = [AllowAny]

class StopFilter(filters.FilterSet):

    # I create own filter to search exactly stop_id
    stop_id = filters.CharFilter(field_name='stop_id', lookup_expr='exact')

    class Meta:
        model = Stop
        fields = ['stop_id']

@api_view(['GET'])
def stop_detail(request):
    queryset = Stop.objects.all()
    stop_filter = StopFilter(request.GET, queryset=queryset)
    filtered_queryset = stop_filter.qs
    serializer = StopsSerializer(filtered_queryset, many=True)

    def fetch_gtfs_files_from_redis():
        try:
            # Fetches all keys from Redis, filters out keys ending with ':hash', decodes them to strings, and returns the list of remaining keys.
            all_keys = client.keys('*')
            gtfs_keys = []
            
            for key in all_keys:
                decoded_key = key.decode('utf-8')
                
                if not decoded_key.endswith(':hash'):
                    gtfs_keys.append(decoded_key)

            return gtfs_keys
        
        except Exception as e:
            return {'error': 'There was an error ' + str(e)}

    def load_gtfs_feed_from_redis(filename):
        try:
            file_content = client.get(filename)
            if file_content:

                # Use a temporary file to handle the GTFS data
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(file_content)
                    temp_file_path = temp_file.name

                try:

                    # Load GTFS data from the temporary file
                    feed = gk.feed.read_feed(path_or_url=temp_file_path, dist_units='km')
                    return feed
                except Exception as e:
                    return {'error': f'Error loading GTFS feed from {temp_file_path}: {e}'}
                finally:

                    # Remove the temporary file
                    os.remove(temp_file_path)
            else:
                return {'error': f'File {filename} not found in Redis.'}
        except Exception as e:
            return {'error': f'Error loading GTFS feed from Redis: {e}'}
    
    def extract_date_from_filename(filename):
        try:

            # Extract date from the filename (e.g., '20240907_20240930.zip')
            date_str = filename.split('_')[0]

            # Convert string to date object
            return datetime.strptime(date_str, '%Y%m%d')
        except ValueError:

            # If the date format is invalid, skip this file
            return None    

    gtfs_files = fetch_gtfs_files_from_redis()
    if not gtfs_files:
        return Response({'message': 'No GTFS files available in Redis.'}, 404)

    gtfs_files_filtered = []
    for file in gtfs_files:
        date = extract_date_from_filename(file)

        if date is not None:
            gtfs_files_filtered.append(file)

    gtfs_files_sorted = sorted(gtfs_files_filtered, key=extract_date_from_filename, reverse=True)

    for gtfs_file in gtfs_files_sorted:
        feed = load_gtfs_feed_from_redis(gtfs_file)
        if feed:
            stop_times_df = feed.stop_times
            trips_df = feed.trips
            
            filtered_by_stops_id = stop_times_df[stop_times_df['stop_id'] == request.GET.get('stop_id')]
            trip_id_by_stops = pd.merge(filtered_by_stops_id, trips_df, on='trip_id')
            
            final_df = trip_id_by_stops[['route_id', 'direction_id']].drop_duplicates()
            route_direction_list = final_df.to_dict(orient='records')

            response = {
                'stops_data': serializer.data,
                'routes': route_direction_list
                
            }
            return Response(response)

    return Response({'message': 'No valid GTFS files found.'}, status=404)

@api_view(["GET"])
def bus_list(request):
    
    def fetch_gtfs_files_from_redis():
        try:
            # Fetches all keys from Redis, filters out keys ending with ':hash', decodes them to strings, and returns the list of remaining keys.
            all_keys = client.keys('*')
            gtfs_keys = []
            
            for key in all_keys:
                decoded_key = key.decode('utf-8')
                
                if not decoded_key.endswith(':hash'):
                    gtfs_keys.append(decoded_key)

            return gtfs_keys
        
        except Exception as e:
            return {'error': 'There was an error ' + str(e)}

    def load_gtfs_feed_from_redis(filename):
        try:
            file_content = client.get(filename)
            if file_content:

                # Use a temporary file to handle the GTFS data
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(file_content)
                    temp_file_path = temp_file.name

                try:

                    # Load GTFS data from the temporary file
                    feed = gk.feed.read_feed(path_or_url=temp_file_path, dist_units='km')
                    return feed
                except Exception as e:
                    return {'error': f'Error loading GTFS feed from {temp_file_path}: {e}'}
                finally:

                    # Remove the temporary file
                    os.remove(temp_file_path)
            else:
                return {'error': f'File {filename} not found in Redis.'}
        except Exception as e:
            return {'error': f'Error loading GTFS feed from Redis: {e}'}
    
    def extract_date_from_filename(filename):
        try:

            # Extract date from the filename (e.g., '20240907_20240930.zip')
            date_str = filename.split('_')[0]

            # Convert string to date object
            return datetime.strptime(date_str, '%Y%m%d')
        except ValueError:

            # If the date format is invalid, skip this file
            return None    

    gtfs_files = fetch_gtfs_files_from_redis()
    if not gtfs_files:
        return Response({'message': 'No GTFS files available in Redis.'}, 404)

    gtfs_files_filtered = []
    for file in gtfs_files:
        date = extract_date_from_filename(file)

        if date is not None:
            gtfs_files_filtered.append(file)

    gtfs_files_sorted = sorted(gtfs_files_filtered, key=extract_date_from_filename, reverse=True)

    bus_ids = []

    for gtfs_file in gtfs_files_sorted:
        feed = load_gtfs_feed_from_redis(gtfs_file)
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
        return Response(response)
    
    return Response({'message': 'No valid GTFS files found.'}, status=404)
    
    # try:
    #     # Download all Route objects
    #     trips = Trip.objects.all()
    #     bus_ids = set()
    #     logger.info(trips)
    #     if not trips.exists():
    #         return Response({'error': 'No trips found'}, 404)
        
    #     # Adding route_id to list
    #     for trip in trips:
    #         route_id = trip.route.route_id
            
    #         # Bus have 3 elements in name
    #         if route_id == '201' or route_id == '202':
    #             continue
    #         elif len(route_id) == 3:
    #             bus_ids.add(route_id)
    #     logger.info(bus_ids)
    #     if not bus_ids:
    #         return Response({'message': 'No bus IDs found with 3 characters'})
        
    #     return Response(list(bus_ids), 200)
    
    # except Route.DoesNotExist:
    #     return Response({'error': 'Route not found'}, status=404)
    # except Exception as e:
    #     return Response({'error': str(e)}, 500)

@api_view(["GET"])
def tram_list(request):

    def fetch_gtfs_files_from_redis():
        try:
            # Fetches all keys from Redis, filters out keys ending with ':hash', decodes them to strings, and returns the list of remaining keys.
            all_keys = client.keys('*')
            gtfs_keys = []
            
            for key in all_keys:
                decoded_key = key.decode('utf-8')
                
                if not decoded_key.endswith(':hash'):
                    gtfs_keys.append(decoded_key)

            return gtfs_keys
        
        except Exception as e:
            return {'error': 'There was an error ' + str(e)}

    def load_gtfs_feed_from_redis(filename):
        try:
            file_content = client.get(filename)
            if file_content:

                # Use a temporary file to handle the GTFS data
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(file_content)
                    temp_file_path = temp_file.name

                try:

                    # Load GTFS data from the temporary file
                    feed = gk.feed.read_feed(path_or_url=temp_file_path, dist_units='km')
                    return feed
                except Exception as e:
                    return {'error': f'Error loading GTFS feed from {temp_file_path}: {e}'}
                finally:

                    # Remove the temporary file
                    os.remove(temp_file_path)
            else:
                return {'error': f'File {filename} not found in Redis.'}
        except Exception as e:
            return {'error': f'Error loading GTFS feed from Redis: {e}'}
    
    def extract_date_from_filename(filename):
        try:

            # Extract date from the filename (e.g., '20240907_20240930.zip')
            date_str = filename.split('_')[0]

            # Convert string to date object
            return datetime.strptime(date_str, '%Y%m%d')
        except ValueError:

            # If the date format is invalid, skip this file
            return None    

    gtfs_files = fetch_gtfs_files_from_redis()
    if not gtfs_files:
        return Response({'message': 'No GTFS files available in Redis.'}, 404)

    gtfs_files_filtered = []
    for file in gtfs_files:
        date = extract_date_from_filename(file)

        if date is not None:
            gtfs_files_filtered.append(file)

    gtfs_files_sorted = sorted(gtfs_files_filtered, key=extract_date_from_filename, reverse=True)

    tram_ids = []

    for gtfs_file in gtfs_files_sorted:
        feed = load_gtfs_feed_from_redis(gtfs_file)
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
        return Response(response)
    
    return Response({'message': 'No valid GTFS files found.'}, status=404)



    # try:
    #     # Download all Route objects
    #     trips = Trip.objects.all()

    #     tram_ids = []

    #     if not trips.exists():
    #         return Response({'error': 'No trips found'}, 404)
        
    #     # Adding route_id to list
    #     for trip in trips:
    #         route_id = {'route_id': trip.route.route_id}
            
    #         # Tram have 1 or 2 elements in name
    #         if len(route_id['route_id']) <= 2:
    #             tram_ids.append(route_id)
    #         elif route_id['route_id'] == '201' or route_id['route_id'] == '202':
    #             tram_ids.append(route_id)
        
    #     if not tram_ids:
    #         return Response({'message': 'No tram IDs found with 3 characters'})
        
    #     return Response(tram_ids, 200)
    
    # except Route.DoesNotExist:
    #     return Response({'error': 'Route not found'}, status=404)
    # except Exception as e:
    #     return Response({'error': str(e)}, 500)

# @api_view(['GET'])
# def trip_detail(request, route_id):
#     # Instantiate the service with the necessary route_id
#     service = GTFSService(route_id=route_id, stop_id=None, direction_id=None, current_day_of_week=None)

#     # Fetch the trip details
#     trip_data = service.get_trip_details()

#     if trip_data:
#         return Response(trip_data, 200)
#     else:
#         return Response({'message': 'No trip data found for the given route.'}, 404)

@api_view(['GET'])
def trip_detail(request, route_id):
    # --> trips.txt contain route_id and trips_id --> 

    # -- > stop_times.txt contain trip ID and stops_id in order(stop_sequence) -->
    
    # --> stops.txt contain stops_id and stops_name

    # Getting data from redis

    
    try:
        stop_times_key = 'stop_times.txt'
        trips_key = 'trips.txt'
        stops_key = 'stops.txt'
        
        try:
            stop_times_data = client.get(stop_times_key).decode('utf-8')
            trips_data = client.get(trips_key).decode('utf-8')
            stops_data = client.get(stops_key).decode('utf-8')

        except (ConnectionError, TimeoutError) as e:
            return Response({'error': 'Error retrieving data from the client.'}, 500)

        stop_times_csv = csv.DictReader(StringIO(stop_times_data))
        trips_csv = csv.DictReader(StringIO(trips_data))
        stops_csv = csv.DictReader(StringIO(stops_data))

        routes = {}
        stops_dict = {}

        # Itereting data from trips.txt to get trip_id
        try:
            for trips in trips_csv:
                trips_route_id = trips['route_id']
                direction_id = trips['direction_id']
                if trips_route_id == route_id:
                    trip_id = trips['trip_id']
                    routes[trip_id] = {
                        'direction_id': direction_id,
                        'stops_detail': []
                    }
            
        
        except KeyError as e:
            return Response({'error': f'Missing key in trips data: {e}'}, 500)

        # Itereting data from stop_times.txt to get departure time and trip_id
        try:   
            for stop_times in stop_times_csv:
                stop_times_trip_id = stop_times['trip_id']
                stop_times_stop_id = stop_times['stop_id']

                # Check that stop_times_trip_id is the same like in trip_id in routes
                if stop_times_trip_id in routes:
                    routes[stop_times_trip_id]['stops_detail'].append({
                        'stop_id': stop_times_stop_id,
                    })
        
        except KeyError as e:
            return Response({'error': f'Missing key in stop_times data: {e}'}, 500)
        
        # Make dict with stops
        try:      
            for stops in stops_csv:
                stop_id = stops['stop_id']
                stop_name = stops['stop_name']
                stops_dict[stop_id] = stop_name
            
        except KeyError as e:
            return Response({'error': f'Missing key in stops data: {e}'},  500)
        
        # Map stop_ids to stop_names
        try: 
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
            
                
        except KeyError as e:
            return Response({'error': f'Error mapping stop_ids to stop_names: {e}'}, 500)
        
        # Get sequences of stops
        try:
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
        except KeyError as e:
            return Response({'error': f'Error generating sequences: {e}'},  500)

        # Create pattern and identifie as the most popular for each direciton_id
        try:
            patterns_count = {}
            for sequence, data in sequences.items():
                direction_id = data['direction_id']
                count = len(data['trip_ids'])

                # Add patterns that get more than 2 reapets
                if count > 1:
                    if direction_id not in patterns_count:
                        patterns_count[direction_id] = {
                            'stops': data['stops'],
                            'count': count
                        }
                    else:
                        # Check that the pattren is the most popular
                        if count > patterns_count[direction_id]['count']:
                            patterns_count[direction_id] = {
                                'stops': data['stops'],
                                'count': count
                            }


            response_data = {
                
                "route id": route_id,
                "most_popular_patterns": {}
            }
            for direction_id, pattern in patterns_count.items():
                response_data["most_popular_patterns"][direction_id] = {
                    'stops': pattern['stops'],
                }
        
        except Exception as e:
            return Response({'error': f'Error creating patterns: {e}'},  500)

        return Response(response_data, 200)

    except Exception as e:
        # Handle and log the exception
        return Response({"error": str(e)}, 500)

@api_view(['GET'])
def schedule(request, route_id, stop_id, direction_id):
    # Request day parameter
    day_of_week = request.GET.get('day', None)
    days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    
    if day_of_week is not None:
        if day_of_week not in days_of_week:
            return Response({"error": f"Invalid day of the week. Valid values are: {', '.join(days_of_week)}."}, 404)
    
    # Get the current day of the week, if there is no request day
    current_day_of_week = day_of_week or days_of_week[datetime.today().weekday()]

    # Cast direction_id to an integer
    direction_id = int(direction_id)

    # Initialize GTFSService to handle logic
    gtfs_service = GTFSService(route_id, stop_id, direction_id, current_day_of_week)
    
    try:
        schedule_data = gtfs_service.get_schedule()
        
        if schedule_data:
            return Response(schedule_data, 200)
        else:
            return Response({'message': 'No schedule found for the given route and stop.'}, 404)
    
    except Exception as e:
        return Response({'error': f'Unexpected error: {str(e)}'}, 500)




# @api_view(['GET'])
# def schedule(request, route_id, stop_id, direction_id):
#     def fetch_gtfs_files_from_redis():
#         try:
#             # Fetches all keys from Redis, filters out keys ending with ':hash', decodes them to strings, and returns the list of remaining keys.
#             all_keys = client.keys('*')
#             gtfs_keys = []
            
#             for key in all_keys:
#                 decoded_key = key.decode('utf-8')
                
#                 if not decoded_key.endswith(':hash'):
#                     gtfs_keys.append(decoded_key)

#             return gtfs_keys
        
#         except Exception as e:
#             return {'error': 'There was an error ' + str(e)}

#     def load_gtfs_feed_from_redis(filename):
#         try:
#             file_content = client.get(filename)
#             if file_content:

#                 # Use a temporary file to handle the GTFS data
#                 with tempfile.NamedTemporaryFile(delete=False) as temp_file:
#                     temp_file.write(file_content)
#                     temp_file_path = temp_file.name

#                 try:

#                     # Load GTFS data from the temporary file
#                     feed = gk.feed.read_feed(path_or_url=temp_file_path, dist_units='km')
#                     return feed
#                 except Exception as e:
#                     return {'error': f'Error loading GTFS feed from {temp_file_path}: {e}'}
#                 finally:

#                     # Remove the temporary file
#                     os.remove(temp_file_path)
#             else:
#                 return {'error': f'File {filename} not found in Redis.'}
#         except Exception as e:
#             return {'error': f'Error loading GTFS feed from Redis: {e}'}

#     def extract_date_from_filename(filename):
#         try:

#             # Extract date from the filename (e.g., '20240907_20240930.zip')
#             date_str = filename.split('_')[0]

#             # Convert string to date object
#             return datetime.strptime(date_str, '%Y%m%d')
#         except ValueError:

#             # If the date format is invalid, skip this file
#             return None    
    
#     # Night routes have time 24:00, 25:00, 26:00, 27:00, 28:00
#     def convert_time(departure_time):
#         pattern = re.compile(r"(2[4-9]):([0-5][0-9])")

#         match = pattern.match(departure_time)
#         if match:
#             hour = int(match.group(1))
#             new_hour = hour - 24
#             return f"{new_hour}:{match.group(2)}"
        
#         return departure_time
    
#     # Request day parameter
#     day_of_week = request.GET.get('day', None)

#     # Define days of the week
    
#     days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
#     if day_of_week is not None:
#         if day_of_week not in days_of_week:
#             return Response({"error": f"Invalid day of the week. Valid values are: {', '.join(days_of_week)}."}, 404)
    
#     # Get the current day of the week, if there is no request day
#     current_day_of_week = day_of_week or days_of_week[datetime.today().weekday()]

#     # Cast direction_id to an integer
#     direction_id = int(direction_id)

#     # Fetch GTFS files from Redis
#     gtfs_files = fetch_gtfs_files_from_redis()

#     if not gtfs_files:
#         return Response({'message': 'No GTFS files available in Redis.'}, 404)

#     # Filter and sort GTFS files based on date extracted from filename
#     gtfs_files_filtered = []
#     for file in gtfs_files:
#         date = extract_date_from_filename(file)

#         if date is not None:
#             gtfs_files_filtered.append(file)

#     gtfs_files_sorted = sorted(gtfs_files_filtered, key=extract_date_from_filename, reverse=True)

#     day_dataframes = {}

#     for day in days_of_week:
#         day_dataframes[day] = None

#     for gtfs_file in gtfs_files_sorted:
#         feed = load_gtfs_feed_from_redis(gtfs_file)

#         if not feed:
#             continue

#         # Extract dataframes from GTFS feed
#         calendar_df = feed.calendar
#         trips_df = feed.trips
#         stop_times_df = feed.stop_times
#         stops_df = feed.stops
#         calendar_dates_df = feed.calendar_dates
        
#         today_date = datetime.today().date()

#         # Check excpetion from calendar_dates
#         if calendar_dates_df is not None and not calendar_dates_df.empty:
#             date_exceptions = calendar_dates_df[calendar_dates_df['date'] == today_date]

#             # Check for exceptions
#             active_exceptions = date_exceptions[date_exceptions['exception_type'] == 1]
#             deactivated_exceptions = date_exceptions[date_exceptions['exception_type'] == 2]
#         else:
#             active_exceptions = pd.DataFrame()
#             deactivated_exceptions = pd.DataFrame()

#         if day_dataframes[current_day_of_week] is None:
            
#             # Filter active services based on the current day
#             active_services = calendar_df[calendar_df[current_day_of_week] == 1]

#             # Activate exceptions to active service_id
#             if not active_exceptions.empty:
#                 active_services = pd.concat([
#                     active_services,
#                     active_exceptions.merge(calendar_df, on='service_id', how='left')
#                 ]).drop_duplicates('service_id')

#             # Delete deactivated service_id
#             if not deactivated_exceptions.empty:
#                 active_services = active_services[~active_services['service_id'].isin(deactivated_exceptions['service_id'])]

#             if not active_services.empty:

#                 # Merge dataframes to get the full schedule
#                 trips_on_day = pd.merge(active_services, trips_df, on='service_id')
#                 stop_times_on_day = pd.merge(trips_on_day, stop_times_df, on='trip_id')
#                 full_schedule = pd.merge(stop_times_on_day, stops_df, on='stop_id')

#                 # Filter schedule based on the given variables
#                 full_schedule_filtered = full_schedule[
#                     (full_schedule['stop_id'] == stop_id) & 
#                     (full_schedule['route_id'] == route_id) &
#                     (full_schedule['direction_id'] == direction_id)
#                 ]
#                 day_dataframes[current_day_of_week] = full_schedule_filtered
                

#         if day_dataframes[current_day_of_week] is not None:
#             break

#     if day_dataframes[current_day_of_week] is not None:
#         # Prepare final dataframe for the response
#         final_df = day_dataframes[current_day_of_week][['route_id', 'departure_time', 'start_date', 'stop_id', 'direction_id', 'trip_id', 'stop_headsign', 'stop_name']].sort_values(by='departure_time')

#         # Regex function and removec seconds
#         final_df['departure_time'] = final_df['departure_time'].apply(convert_time).str.slice(0, 5)
#         stop_headsign = final_df['stop_headsign'].iloc[0]
#         stop_name = final_df['stop_name'].iloc[0]


#         current_day_info = {
#             'current_day': current_day_of_week,
#             'schedules' : final_df.to_dict(orient='records'),
#             'stop_name': stop_name,
#             'stop_headsign': stop_headsign
#         }
#         response_data = current_day_info
#         return Response(response_data, 200)
#     else:
#         return Response({'message': 'No schedule found for the given route and stop.'}, 404)


# -----------------------------------------------------------------------------TEST API ---------------------------------------------------------------------------------------------------------------

def home(request):
    return HttpResponse(f"Hello")


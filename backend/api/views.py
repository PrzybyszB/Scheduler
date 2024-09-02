from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from .models import Profile, Premium, Route, Trip, Stop
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
# from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import ProfileSerializer, UserSerializer, PremiumSerializer, RouteSerializer, TripSerializer
from .tasks import client
import json


class APIRoot(APIView):
    def get(self, request, format=None):
        return Response({
            'register': '/api/register/',
            'profiles list': '/api/profile-list/',
            'profile detail': '/api/profile/<int:pk>',
            'user detail': '/api/user/<int:pk>',
            'users list': '/api/user-list/',
            'premium create': '/api/premium/create',
            'premium delete': '/api/premium/delete/<int:pk>',
            'premium list': '/api/premium/list',
            'cart': '/api/cart/',
            'transport_detail' : 'api/<str:route_id>', 
            'tram list' : 'api/tram-list',
            'bus list' : 'api/bus-list',
            'stops list' : 'api/stops-list',

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

@api_view(["GET"])
def stops_list(request):
    stops = Stop.objects.all().order_by('stop_name')
    stops_list = []

    if not stops.exists():
        return Response({'error' : 'No stops found' }, 404)
    
    for stop in stops:
        stop_name = {'stop_name' : stop.stop_name}
        stops_list.append(stop_name)

    return Response(stops_list, 200)

@api_view(["GET"])
def bus_list(request):
    try:
        # Download all Route objects
        routes = Route.objects.all().order_by('route_id')
        bus_ids = []

        if not routes.exists():
            return Response({'error': 'No routes found'}, 404)
        
        # Adding route_id to list
        for route in routes:
            route_id = {'route_id': route.route_id}
            # Bus have 3 elements in name
            if len(route_id['route_id']) == 3:
                bus_ids.append(route_id)
        
        if not bus_ids:
            return Response({'message': 'No bus IDs found with 3 characters'})
        
        return Response(bus_ids, 200)
    
    except Route.DoesNotExist:
        return Response({'error': 'Route not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, 500)

@api_view(["GET"])
def tram_list(request):
    try:
        # Download all Route objects
        routes = Route.objects.all()

        tram_ids = []

        if not routes.exists():
            return Response({'error': 'No routes found'}, 404)
        
        # Adding route_id to list
        for route in routes:
            route_id = {'route_id': route.route_id}
            
            # Tram have 1 or 2 elements in name
            if len(route_id['route_id']) in [1,2]:
                tram_ids.append(route_id)
        
        if not tram_ids:
            return Response({'message': 'No tram IDs found with 3 characters'})
        
        return Response(tram_ids, 200)
    
    except Route.DoesNotExist:
        return Response({'error': 'Route not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, 500)

@api_view(['GET'])
def transport_detail(request, id):
    
    # --> trips.txt contain route_id and trips_id --> 

    # -- > stop_times.txt contain trip ID and stops_id in order(stop_sequence) -->
    
    # --> stops.txt contain stops_id and stops_name

    # Getting data from redis
    try:
        stop_times_key = 'stop_times.txt'
        trips_key = 'trips.txt'
        stops_key = 'stops.txt'
        
        try:
            stop_times_data = client.get(stop_times_key)
            trips_data = client.get(trips_key)
            stops_data = client.get(stops_key)
        except (ConnectionError, TimeoutError) as e:
            return Response({'error': 'Error retrieving data from the client.'}, status=500)

        try:
            stop_times_json_data = json.loads(stop_times_data)
            trips_json_data = json.loads(trips_data)
            stops_json_data = json.loads(stops_data)
        except json.JSONDecodeError as e:
            return Response({'error': 'Error decoding JSON data.'}, status=500)

        routes = {}
        stops_dict = {}

        # Itereting data from trips.txt to get trip_id
        try:
            for trips in trips_json_data:
                trips_route_id = trips['route_id']
                if trips_route_id == id:
                    trip_id = trips['trip_id']
                    routes[trip_id]= {'stops_detail' : []}
        except KeyError as e:
            return Response({'error': f'Missing key in trips data: {e}'}, status= 500)

        # Itereting data from stop_times.txt to get departure time and trip_id
        try:   
            for stop_times in stop_times_json_data:
                stop_times_trip_id = stop_times['trip_id']
                stop_times_stop_id = stop_times['stop_id']

                # Check that stop_times_trip_id is the same like in trip_id in routes
                if stop_times_trip_id in routes:
                    routes[stop_times_trip_id]['stops_detail'].append({
                        'stop_id': stop_times_stop_id,
                })
        except KeyError as e:
            return Response({'error':f'Missing key in stop_times data: {e}'}, status= 500)
        
        # Make dict with stops
        try:      
            for stops in stops_json_data:
                stop_id = stops['stop_id']
                stop_name = stops['stop_name']
                stops_dict[stop_id] = stop_name
        except KeyError as e:
            return Response({'error':f'Missing key in stops data: {e}'}, status= 500)

        # Map stop_ids to stop_names
        try: 
            for trip_id, trip_info in routes.items():
                stop_names = []
                for detail in trip_info['stops_detail']:
                    stop_id = detail['stop_id']
                    stop_name = stops_dict.get(stop_id, None)
                    if stop_name:
                        stop_names.append({
                            'stop_name': stop_name,
                            })
                routes[trip_id] = {'stops_detail': stop_names}
        except KeyError as e:
            return Response({'error':f'Error mapping stop_ids to stop_names: {e}'}, status= 500)
        
        # Get sequences of stops
        try:
            sequences = {}    
            for trip_id, trip_data in routes.items():

                # Making a list with stops name 
                stop_names = []
                for stop in trip_data['stops_detail']:
                    stop_name = stop['stop_name']
                    stop_names.append(stop_name)
                    
                # Making a tuple to get IDS(stop_ids) for sequence
                sequence = tuple(stop_names)

                if sequence not in sequences:
                    sequences[sequence] = {
                        "trip_ids": [],
                        'stops': stop_names
                        }
                        
                sequences[sequence]["trip_ids"].append(trip_id)
        except KeyError as e:
            return Response({'error': f'Error generating sequences:{e}'}, status= 500)
        

        # Creating patterns from the stop sequences and identifying the two most frequently occurring ones.
        try:
            items = list(sequences.items())
            patterns_result = []
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

            patterns_result.sort(key=lambda x: x['counter'], reverse=True)
            common_patterns =  patterns_result[:2]
        except KeyError as e:
            return Response({'error': f'Error creating patterns: {e}'}, status= 500)
        except IndexError as e:
            return Response({'error': 'Not enough patterns found.'}, status= 500)

        # Return only two most common routes and their first stops as most_common_routes[0][0] and most_common_routes[1][0]
        response_data = {}
        for pattern in common_patterns:
            most_common_routes = pattern.get('stops_display')
            response_data = {
                "id": id,
                most_common_routes[0][0]: most_common_routes[0],
                most_common_routes[1][0] : most_common_routes [1]
            }

        return Response(response_data)

    except Exception as e:
        # Handle and log the exception
        print(f"An error occurred: {e}")
        return Response({"error": str(e)}, status=500)








# -----------------------------------------------------------------------------TEST API ---------------------------------------------------------------------------------------------------------------
@api_view(['GET'])
def api_test_16(request):
    route_16 = Route.objects.get(route_id = 16)
    serializer_class = RouteSerializer(route_16)
    return Response(serializer_class.data)

def api_test_16_rt(request):
    trip_updates_key = 'trip_updates'
    feeds_key = 'feeds'
    vehicle_positions_key = 'vehicle_positions'

    trip_update_data = client.get(trip_updates_key)
    feeds_data = client.get(feeds_key)
    vehicle_positions_data = client.get(vehicle_positions_key)

    trip_update_json = json.loads(trip_update_data)
    feeds_json = json.loads(feeds_data)
    vehicle_positions_json = json.loads(vehicle_positions_data)

    positions = []


    for entity_vehicle in vehicle_positions_json['entity']:
        vehicle = entity_vehicle['vehicle']
        trip = vehicle['trip']
        route_id = trip['routeId']
        
        if route_id == "16":
            position = vehicle['position']
            positions.append(position)
            
            # for entity_trip in trip_update_json['entity']:
            #     trip_update = entity_trip['tripUpdate']
            #     trip = trip_update['trip']
            #     trip_route_id = trip['routeId']
                
            #     if trip_route_id == "16":
            #         stopTimeUpdate = trip_update['stopTimeUpdate']
            #         for stop_update in stopTimeUpdate:
            #             arrival = stop_update['arrival']
            #             delay = arrival['delay']
            #             if entity_vehicle['id'] == entity_trip['id']:
            #                 break
        
    return HttpResponse(f"Hello its me 16 tramwaj and my pozycja :Position: {positions}")

@api_view(['GET'])
def api_test_RT(request):
    keys = ['trip_updates', 'feeds', 'vehicle_positions']
    timestamps = []

    for key in keys:
        data = client.get(key)
        
        try:
            json_data = json.loads(data)
            timestamp = json_data['header']['timestamp']
            timestamps.append(timestamp)
        except KeyError:
            return HttpResponse(f'No timestamp found for key: {key}', status=404)
        except json.JSONDecodeError as e:
            return HttpResponse(f'Error decoding JSON: {str(e)}', status=500)
        
    return HttpResponse(', '.join(timestamps))


def home(request):
    return HttpResponse(f"Hello")


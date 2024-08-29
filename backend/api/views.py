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

    # stop_times.txt contain trip ID and stops_id in order(stop_sequence) and last stop(stop_headsign)
    
    # --> trips.txt with Trip ID contain route_id --> route_id

    

    stop_times_key = 'stop_times.txt'
    trips_key = 'trips.txt'
    stops = 'stops.txt'
    
    stop_times_data = client.get(stop_times_key)
    trips_data = client.get(trips_key)
    stops_data = client.get(stops)

    stop_times_json_data = json.loads(stop_times_data)
    trips_json_data = json.loads(trips_data)
    stops_json_data = json.loads(stops_data)

    routes = {}
    stops_dict = {}

    

    for trips in trips_json_data:
        trips_route_id = trips['route_id']
        if trips_route_id == id:
            trip_id = trips['trip_id']
            trip_headsign = trips['trip_headsign']
            routes[trip_id]= {
                'trip_headsign' : trip_headsign,
                'stops_detail' : []
            }

    for stop_times in stop_times_json_data:
        stop_times_trip_id = stop_times['trip_id']
        stop_times_stop_id = stop_times['stop_id']
        departure_time = stop_times['departure_time']

        if stop_times_trip_id in routes:
            routes[stop_times_trip_id]['stops_detail'].append({
                'stop_id': stop_times_stop_id,
                'departure_time': departure_time,
            
        })
            
    
    for stops in stops_json_data:
        stop_id = stops['stop_id']
        stop_name = stops['stop_name']
        stops_dict[stop_id] = stop_name

    for trip_id, trip_info in routes.items():
        stop_names = []
        for detail in trip_info['stops_detail']:
            stop_id = detail['stop_id']
            departure_time = detail['departure_time']
            stop_name = stops_dict.get(stop_id, None)
            if stop_name:
                stop_names.append({
                    'stop_id': stop_id,
                    'stop_name': stop_name,
                    'departure_time': departure_time,
                    })
        routes[trip_id] = {
            'trip_headsign': trip_info['trip_headsign'],
            'stops_detail': stop_names
        }
    
    def get_stop_sequences(routes):
        sequences = {}
        
        for trip_id, trip_data in routes.items():

            trip_headsign = trip_data['trip_headsign']
            # print(f"Trip ID: {trip_id}, Headsign: {headsign}")

            stop_ids = []
            stop_names = []

            for stop in trip_data['stops_detail']:
                stop_id = stop['stop_id']
                stop_name = stop['stop_name']
                stop_ids.append(stop_id)
                stop_names.append(stop_name)
            
            # Making a tuple to get IDS(stop_ids) for sequence
            sequence = tuple(stop_ids)

            if sequence not in sequences:
                sequences[sequence] = {
                    "trip_ids": [],
                    "trip_headsign": trip_headsign,
                    "stops_details": []
                    }
                
            sequences[sequence]["trip_ids"].append(trip_id)

            stop_descriptions = []
            for i in range(len(stop_ids)):
                stop_id = stop_ids[i]
                stop_name = stop_names[i]
                stop_descriptions.append((stop_id, stop_name))
            

            sorted_stops = []
            for stop_id in stop_ids:
                for stop in stop_descriptions:
                    if stop[0] == stop_id:
                        sorted_stops.append(f'{stop[0]} = {stop[1]}')
            
            sequences[sequence]["stops"] = sorted_stops
        
        return sequences

    def find_common_patterns(sequences):
        items = list(sequences.items())
        patterns_counter = []
        patterns_result = []
        index = 1

        for pattern, data in items:
            stops_display = ", ".join(data['stops'])
            trip_ids_display = ", ".join(data['trip_ids'])
            trip_headsign = data['trip_headsign']

            counter = len(data['trip_ids'])
            patterns_counter.append(counter)

            pattern_info = {
                'pattern_index': index,
                'stops_display': stops_display,
                'trip_headsign': trip_headsign,
                'counter': counter,
                'trips_ids': trip_ids_display 
            }
            patterns_result.append(pattern_info)

            index += 1

        # two_most_common_pattern = sorted(patterns_counter, reverse=True)[:2]

        return patterns_result

    sequences = get_stop_sequences(routes)
    common_patterns = find_common_patterns(sequences)

    stop_display_data = []
    for pattern in common_patterns:
        stops_pattern = pattern['stops_display']
        counter = pattern['counter']
        stop_display_data.append((stops_pattern,counter))


    
    response_data = {
        "patterns": stop_display_data,
    }

    return Response(response_data)










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


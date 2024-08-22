from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from .models import Profile, Premium, Route, Trip
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
def bus_list(request):
    try:
        # Download all Route objects
        routes = Route.objects.all()
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


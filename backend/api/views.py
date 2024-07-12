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
    # permission_classes = [AllowAny]

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    # permission_classes = [AllowAny]

class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [AllowAny]

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [AllowAny]

class PremiumCreate(generics.CreateAPIView):
    queryset = Premium.objects.all()
    serializer_class = PremiumSerializer
    # permission_classes = [AllowAny]

class PremiumDestroy(generics.RetrieveDestroyAPIView):
    queryset = Premium.objects.all()
    serializer_class = PremiumSerializer
    # permission_classes = [AllowAny]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        premium_data = serializer.data
        premium_id = instance.id
        self.perform_destroy(instance)
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


@api_view(['GET'])
def api_test_16(request):
    route_16 = Route.objects.get(route_id = 16)
    # trip_16 = Trip.objects.get(trip_id = "1_3484103^N+" )
    serializer_class = RouteSerializer(route_16)
    # serializer_class = TripSerializer(trip_16)
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

    for entity_vehicle in vehicle_positions_json['entity']:
        vehicle = entity_vehicle['vehicle']
        trip = vehicle['trip']
        route_id = trip['routeId']
        position = vehicle['position']
        
        if route_id == "16":
            for entity_trip in trip_update_json['entity']:
                trip_update = entity_trip['tripUpdate']
                trip = trip_update['trip']
                trip_route_id = trip['routeId']
                
                if trip_route_id == "16":
                    stopTimeUpdate = trip_update['stopTimeUpdate']
                    for stop_update in stopTimeUpdate:
                        arrival = stop_update['arrival']
                        delay = arrival['delay']
                        if entity_vehicle['id'] == entity_trip['id']:
                            break
                        
    return HttpResponse(f"Hello its me 16 tramwaj and my pozycja :Position: {position}")

# @api_view(['GET'])
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

# @api_view(['GET'])
# def api_user_list(request):
#     user_list = User.objects.all()
#     serializer_class = UserSerializer(user_list, many=True)
#     # permission_classes = [AllowAny]
#     return Response(serializer_class.data)

def home(request):
    return HttpResponse(f"Hello")
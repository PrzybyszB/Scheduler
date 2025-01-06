import logging
from django.http import HttpResponse
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import ProfileSerializer, UserSerializer, PremiumSerializer, StopsSerializer
from .models import Profile, Premium, Stop
from .services.get_schedule import get_schedule_from_redis, get_valid_day_of_week
from .services.premium import delete_premium
from .services.trip_detail import get_trip_detail
from .services.tram_list import get_tram_list
from .services.bus_list import get_bus_list
from .services.stop_detail import get_stop_detail
from api.filters import StopFilter



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
        premium_data = delete_premium(premium)
        return Response(
            {
                "message": f"Premium with ID {premium_data['id']} was deleted",
                "data": premium_data,
            },
            status=status.HTTP_200_OK,
        )

class PremiumList(generics.ListAPIView):
    queryset = Premium.objects.all()
    serializer_class = PremiumSerializer
    # permission_classes = [AllowAny]

@api_view(['GET'])
def stop_detail(request):
    queryset = Stop.objects.all()
    stop_filter = StopFilter(request.GET, queryset=queryset)
    filtered_queryset = stop_filter.qs
    serializer = StopsSerializer(filtered_queryset, many=True)
    try:

        response_data = get_stop_detail(request.GET, filtered_queryset) 

        response = {
            'stops_data': serializer.data,
            'routes': response_data.get('routes', []),
        }

        return Response(response)
    
    except ValueError as e:
        return Response({'message': str(e)}, 404)
    
    except Exception as e:
        return Response({'error': f'Unexpected error: {str(e)}'}, 500)

@api_view(["GET"])
def bus_list(request):

    try:
        bus_ids = get_bus_list()
        return Response(bus_ids, 200)
    
    except ValueError as e:
        return Response({'message': str(e)}, 404)
    
    except Exception as e:
        return Response({'error': f'Unexpected error: {str(e)}'}, 500)
    
@api_view(["GET"])
def tram_list(request):

    try:
        tram_ids = get_tram_list()
        return Response(tram_ids, 200)
    
    except ValueError as e:
        return Response({'message': str(e)}, status=404)
    
    except Exception as e:
        return Response({'error': f'Unexpected error: {str(e)}'}, 500)
    
@api_view(['GET'])
def trip_detail(request, route_id):

    try:
        trip_detail_data = get_trip_detail(route_id)

        return Response(trip_detail_data, 200 if 'error' not in trip_detail_data else 400)
    
    except Exception as e:
        return Response({'error': f'Unexpected error: {str(e)}'}, 500)

@api_view(['GET'])
def schedule(request, route_id, stop_id, direction_id):
    # Request day parameter
    day_of_week = request.GET.get('day', None)
    day = get_valid_day_of_week(day_of_week)

    try:
        schedule_data = get_schedule_from_redis(route_id, stop_id, direction_id, day)

        if schedule_data:
            return Response(schedule_data, 200)
        else:
            return Response({'message': 'No schedule found for the given route and stop.'}, 404)

    except ValueError as e:
        return Response({'message': str(e)}, 404)

    except Exception as e:
        return Response({'error': f'Unexpected error: {str(e)}'}, 500)

# -----------------------------------------------------------------------------TEST API ---------------------------------------------------------------------------------------------------------------

def home(request):
    return HttpResponse(f"Hello")


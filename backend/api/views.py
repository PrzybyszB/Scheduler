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
from google.transit import gtfs_realtime_pb2
import requests



#TODO do byka czemu nie działa (wykuriwa bład NoReverseMatch at /api/) a wszystko pasuje

# class APIRoot(APIView):
#     def get(self, request, format=None):
#         return Response({
#             'profiles': reverse('profile-list', request=request, format=format),
#             'users': reverse('user-list', request=request, format=format),
#             # Dodaj inne endpointy
#         })

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

@api_view(['GET'])
def api_test_RT_trip_updates(request): 
    pass



# @api_view(['GET'])
# def api_user_list(request):
#     user_list = User.objects.all()
#     serializer_class = UserSerializer(user_list, many=True)
#     # permission_classes = [AllowAny]
#     return Response(serializer_class.data)

def home(request):
    return HttpResponse(f"Hello")
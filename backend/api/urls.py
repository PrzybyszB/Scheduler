from django.urls import path
from rest_framework import routers
from .views import APIRoot, CreateUser, UserProfileList, UserProfileDetail, UserDetail, UserList, PremiumCreate, PremiumDelete, PremiumList, bus_list, tram_list, stop_detail, trip_detail, schedule

app_name = "api"


urlpatterns = [
    path('', APIRoot.as_view(), name='api-root'),
    path('user/list', UserList.as_view(), name='user-list'),
    path('register/', CreateUser.as_view(), name='register'),
    path('profile/list', UserProfileList.as_view(), name='profile-list'),
    path('profile/user/<int:pk>/', UserProfileDetail.as_view(), name='profile-detail'),
    path('user/<int:pk>/', UserDetail.as_view(), name='user-detail'),
    path('premium/create/', PremiumCreate.as_view(), name='product-create'),
    path('premium/delete/<int:pk>', PremiumDelete.as_view(), name='product-destroy'),
    path('premium/list/', PremiumList.as_view(), name='premium-list'),
    path('bus-list/', bus_list, name='bus-list'),
    path('tram-list/', tram_list, name='tram-list'),
    path('route/<str:route_id>/', trip_detail, name='trip-details'),
    path('route/<str:route_id>/stop/<str:stop_id>/direction/<str:direction_id>', schedule, name='stops-detail'),
    path('stops/', stop_detail, name='search-stop'),
    

]
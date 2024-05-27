from django.urls import path, include
#from .views import api_user_list
from rest_framework import routers
from .views import APIRoot, CreateUser, UserProfileList, UserProfileDetail, UserDetail, UserList, PremiumCreate, PremiumDestroy, PremiumList

app_name = "api"


urlpatterns = [
    path('', APIRoot.as_view(), name='api-root'),
    path('user-list/', UserList.as_view(), name='user-list'),
    path('register/', CreateUser.as_view(), name='register'),
    path('profile-list/', UserProfileList.as_view(), name='profile-list'),  # Poprawiona nazwa odnośnika
    path('profile/<int:pk>/', UserProfileDetail.as_view(), name='profile-detail'),
    path('user/<int:pk>/', UserDetail.as_view(), name='user-detail'),
    path('premium/create/', PremiumCreate.as_view(), name='product-create'),
    path('premium/destroy/<int:pk>', PremiumDestroy.as_view(), name='product-destroy'),
    path('premium/list/', PremiumList.as_view(), name='premium-list'),

]
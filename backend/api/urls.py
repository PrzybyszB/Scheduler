from django.urls import path, include
from .views import ProfileViewSet, home
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'profile', ProfileViewSet)

urlpatterns = [
    path('', home, name='home'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')), 
]
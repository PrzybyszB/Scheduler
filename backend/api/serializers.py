from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile, Customer, Premium, PublicTransportType, Stop, Order


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = ["id","username", "first_name", "last_name", "email", "address", "address2", "phone", "is_active"]
    
    # Username retrieval method, then we can call username in fields
    def get_username(self, obj): 
        return obj.user.username if obj.user else None

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "first_name", "last_name", "email", "address", "address2", "phone"]

class Premiumerializer(serializers.ModelSerializer):
    class Meta:
        model = Premium
        fields = ["id", "name", "price", "description", "image","is_active"]

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "user", "created_at", "premium", "customer", "address", "phone", "date", "status"]


class PublicTransportTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicTransportType
        fields = ["id", "number", "is_active"]

class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ["id", "name", "tramway_stops", "bus_stops", "is_active",]



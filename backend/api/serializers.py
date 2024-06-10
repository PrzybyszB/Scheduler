from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile, Customer, Premium, Stop, Order

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]

        # Here the "password" field is write_only, which means it will not be returned in API responses.
        extra_kwargs = {"password":{"write_only":True}}

    # Overrides the default object creation method to use create_user, which hashes the password and creates the user in a secure way.

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = ["id","username", "first_name", "last_name", "email", "address", "address2", "phone", "is_delete"]
    
    # Username retrieval method, then we can call username in fields
    def get_username(self, obj): 
        return obj.user.username if obj.user else None

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "first_name", "last_name", "email", "address", "address2", "phone"]

class PremiumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Premium
        fields = ["id", "name", "price", "description", "image", "is_delete"]

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "user", "created_at", "premium", "customer", "address", "phone", "date", "status"]

class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ["id", "name", "tramway_stops", "bus_stops", "is_delete",]





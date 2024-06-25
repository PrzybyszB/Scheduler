from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile, Customer, Premium, Stop, Order, Agency, Route, Calendar, Shape, Trip, StopTime, FeedInfo, ShapeId

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

class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ["agency_id", "agency_name", "agency_url", "agency_timezone", "agency_lang", "agency_phone"]

class StopStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ["stop_id","stop_code","stop_name","stop_lat","stop_lon","zone_id",]

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ["route_id","agency_id","route_short_name","route_long_name","route_desc","route_type","route_color","route_text_color",]

class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = ["service_id","monday","tuesday","wednesday","thursday","friday","saturday","sunday","start_date","end_date",]

class ShapeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shape
        fields = ["shape_id","shape_pt_lat","shape_pt_lon","shape_pt_sequence",]

class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ["route_id","service_id","trip_id","trip_headsign","direction_id","shape_id","wheelchair_accessible","brigade",]

class StopTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StopTime
        fields = ["trip_id","arrival_time","departure_time","stop_id","stop_sequence","stop_headsign","pickup_type","drop_off_type",]

class FeedInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedInfo
        fields = ["feed_publisher_name","feed_publisher_url","feed_lang","feed_start_date","feed_end_date",]

class ShapeIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShapeId
        Fields = ["shapeidcreator_id", "shape_id", 'trip_id']





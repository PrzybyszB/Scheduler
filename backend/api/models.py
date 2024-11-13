import datetime
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    address2 = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=10, blank=True)
    premium = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    address2 = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f'{self.first_name}{self.last_name}'


class Premium(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=6) #9999.99
    description = models.CharField(max_length=250, default='', blank=True, null=True)
    image = models.ImageField(upload_to='uploads/premium/', blank=True)
    is_delete = models.BooleanField(default=False)

    #Add sale stuff
    is_sale = models.BooleanField(default=False)
    sale_price =  models.DecimalField(default=0, decimal_places=2, max_digits=6) #9999.99


    def __str__(self):
        return self.name


class OrderItem(models.Model):
    name = models.ForeignKey(Premium, on_delete=models.CASCADE)
    price = models.FloatField()


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    items = models.ManyToManyField(OrderItem)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    address = models.CharField(max_length=100, default='', blank=True)
    phone = models.CharField(max_length=20, default='',blank=True)
    date = models.DateField(default=datetime.datetime.today)
    ordered = models.BooleanField(default=False)


# GTFS db.models

class Agency(models.Model):
    agency_id = models.CharField(max_length=255, primary_key=True)
    agency_name = models.CharField(max_length=255)
    agency_url = models.URLField()
    agency_timezone = models.CharField(max_length=255)
    agency_lang = models.CharField(max_length=2, blank=True, null=True)
    agency_phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.agency_name

class Stop(models.Model):
    stop_id = models.CharField(max_length=255, primary_key=True, default='default_stop_id')
    stop_code = models.CharField(max_length=255, blank=True, null=True)
    stop_name = models.CharField(max_length=255, blank=True, null=True)
    stop_lat = models.FloatField(blank=True, null=True)
    stop_lon = models.FloatField(blank=True, null=True)
    zone_id = models.CharField(max_length=1)

    def __str__(self):
        return self.stop_name

class Route(models.Model):
    route_id = models.CharField(max_length=1000, primary_key=True)
    agency_id = models.ForeignKey(Agency, on_delete=models.CASCADE)
    route_short_name = models.CharField(max_length=10)
    route_long_name = models.CharField(max_length=255)
    route_desc = models.CharField(max_length=9999)
    route_type = models.IntegerField()
    route_color = models.CharField(max_length=6, blank=True, null=True)
    route_text_color = models.CharField(max_length=6, blank=True, null=True)

    def __str__(self):
        return self.route_short_name

class Calendar(models.Model):
    service_id = models.CharField(max_length=255, primary_key=True)
    monday = models.BooleanField()
    tuesday = models.BooleanField()
    wednesday = models.BooleanField()
    thursday = models.BooleanField()
    friday = models.BooleanField()
    saturday = models.BooleanField()
    sunday = models.BooleanField()
    start_date = models.DateField(default=20240610)
    end_date = models.DateField(default = 20240616)

    def __str__(self):
        return self.service_id
    
class CalendarDate(models.Model):
    service = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    date = models.DateField() 
    exception_type = models.IntegerField()  

    class Meta:
        unique_together = ('service', 'date')

    def __str__(self):
        return self.service

class ShapeId(models.Model):
    shape_id = models.CharField(primary_key=True)
    
    class Meta:
        ordering = ['shape_id']

    def __str__(self):
        return str(self.shape_id)

class Shape(models.Model):
    shape_id = models.ForeignKey(ShapeId, related_name='shapes', on_delete=models.CASCADE)
    shape_pt_lat = models.FloatField()
    shape_pt_lon = models.FloatField()
    shape_pt_sequence = models.IntegerField()

    class Meta:
        ordering = ['shape_id','shape_pt_sequence' ]

    def __str__(self):
        return f"{self.shape_id} - Sequence {self.shape_pt_sequence}"

class Trip(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    service = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    shape = models.ForeignKey(Shape, on_delete=models.CASCADE)
    trip_id = models.CharField(max_length=255, primary_key=True)
    trip_headsign = models.CharField(max_length=255, blank=True, null=True)
    direction_id = models.IntegerField(blank=True, null=True)
    wheelchair_accessible = models.IntegerField()
    brigade = models.IntegerField()
    

    def __str__(self):
        return self.trip_id
    
class StopTime(models.Model):
    trip_id = models.ForeignKey(Trip, on_delete=models.CASCADE)
    arrival_time = models.TimeField()
    departure_time = models.TimeField()
    stop_id = models.ForeignKey(Stop, on_delete=models.CASCADE)
    stop_sequence = models.IntegerField(validators=[MinValueValidator(0)])
    stop_headsign = models.CharField(max_length=255, blank=True, null=True)
    pickup_type = models.IntegerField(blank=True, null=True)
    drop_off_type = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.stop_id

class FeedInfo(models.Model):
    feed_publisher_name = models.CharField(max_length=255)
    feed_publisher_url = models.URLField()
    feed_lang = models.CharField(max_length=10)
    feed_start_date = models.DateField()
    feed_end_date = models.DateField()

    def __str__(self):
        return self.feed_publisher_name
    




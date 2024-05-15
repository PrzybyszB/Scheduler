import datetime
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# Create a Customer Profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    email = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    address2 = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=10, blank=True)
    premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username



# Create a Customer User
class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    email = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    address2 = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f'{self.first_name}{self.last_name}'

# Create a premium Variables
class Premium(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=6) #9999.99
    description = models.CharField(max_length=250, default='', blank=True, null=True)
    image = models.ImageField(upload_to='uploads/premium/')
    is_active = models.BooleanField(default=True)

    #Add sale stuff
    is_sale = models.BooleanField(default=False)
    sale_price =  models.DecimalField(default=0, decimal_places=2, max_digits=6) #9999.99


    def __str__(self):
        return self.name

# Create a premium Variables
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    premium = models.ForeignKey(Premium,on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer,on_delete=models.PROTECT)
    address = models.CharField(max_length=100, default='', blank=True)
    phone = models.CharField(max_length=20, default='',blank=True)
    date = models.DateField(default=datetime.datetime.today)
    status = models.BooleanField(default=False)
    


# Create Tramway
class PublicTransportType(models.Model):
    number = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)


class Stop(models.Model):
    name = models.CharField(max_length=50)
    tramway_stops = models.ForeignKey(PublicTransportType, related_name='tramway_stop_set', on_delete=models.CASCADE)
    bus_stops = models.ForeignKey(PublicTransportType, related_name='bus_stop_set', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

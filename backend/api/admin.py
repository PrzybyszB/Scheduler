from django.contrib import admin
from. models import Profile, Customer, Premium, Order,PublicTransportType, Stop, OrderItem

admin.site.register(Profile)
admin.site.register(Customer)
admin.site.register(Premium)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(PublicTransportType)
admin.site.register(Stop)


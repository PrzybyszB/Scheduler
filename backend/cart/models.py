from django.db import models
from django.contrib.auth.models import User
from api.models import Premium


class CartModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    cart_data = models.JSONField(default=dict, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.item.all())

    def __str__(self):
        return f"Cart {self.id} for {self.user.username}"
    


class CartItem(models.Model):
    cart = models.ForeignKey(CartModel, on_delete=models.PROTECT, related_name='items')
    premium = models.ForeignKey(Premium, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.quantity * self.premium.price
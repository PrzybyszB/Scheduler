import json
from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from api.models import Premium, Profile
import redis

redis_instance = redis.StrictRedis(host='localhost', port=6379, db=0)


class Koszyk:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
        self.cart_id = self.session.get('cart_id')

        if not self.cart_id:
            self.cart_id = self._create_cart()

    def _create_cart(self):
        cart_id = self.redis_instance.incr('cart_id_generator')
        self.session['cart_id'] = cart_id
        self.session.modified = True
        return cart_id

    def add_to_cart(user, premium_id, quantity=1):
    # Dodawanie przedmiotu do koszyka przechowywanego w Redisie
        cart_key = f"cart:{user.id}"
        cart_data = redis_instance.hget(cart_key, premium_id)
        if cart_data:
            cart_data = json.loads(cart_data)
            cart_data['quantity'] += quantity
        else:
            cart_data = {'premium_id': premium_id, 'quantity': quantity}
        
        redis_instance.hset(cart_key, premium_id, json.dumps(cart_data))

        # Synchronizacja danych z modelem Cart w bazie danych PostgreSQL
        cart, _ = Cart.objects.get_or_create(user=user)
        premium = get_object_or_404(Premium, pk=premium_id)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, premium=premium)
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
    def remove_from_cart(self, produkt_id):
        produkt_id = str(produkt_id)
        self.redis_instance.hdel('cart:' + str(self.cart_id), produkt_id)

    def get_cart_items(self):
        cart_data = self.redis_instance.hgetall('cart:' + str(self.cart_id))
        cart_items = {}
        for produkt_id, data in cart_data.items():
            cart_items[int(produkt_id)] = json.loads(data)
        return cart_items

    def clear_cart(self):
        self.redis_instance.delete('cart:' + str(self.cart_id))


    def synchronize_cart_with_db(user):
        cart_key = f"cart:{user.id}"
        cart_data = redis_instance.hgetall(cart_key)
        if cart_data:
            cart, _ = Cart.objects.get_or_create(user=user)
            for premium_id, data in cart_data.items():
                data = json.loads(data)
                premium = get_object_or_404(Premium, pk=premium_id)
                cart_item, created = CartItem.objects.get_or_create(cart=cart, premium=premium)
                if not created:
                    cart_item.quantity += data['quantity']
                    cart_item.save()

















'''
SESSION CART


from django.core.cache import cache
from django.conf import settings
from datetime import timedelta
from api.models import Premium, Profile

class Cart():
    def __init__(self, request):
        self.request = request

        # Unique cache key for the current user or session
        if self.request.user.is_authenticated:
            self.cache_key = f'cart_{self.request.user.id}'
        else:
            self.cache_key = f'cart_{self.request.session.session_key}'

        # Get cart from cache
        self.cart = cache.get(self.cache_key, {})

    def save(self):
        # Set the cart in cache with a timeout
        cache.set(self.cache_key, self.cart, timeout=settings.CART_CACHE_TIMEOUT)

    def add(self, product, quantity):
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id] += quantity
        else:
            self.cart[product_id] = quantity

        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __len__(self):
        return sum(self.cart.values())

    def get_prods(self):
        product_ids = self.cart.keys()
        products = Premium.objects.filter(id__in=product_ids)
        return products

    def get_total(self):
        product_ids = self.cart.keys()
        products = Premium.objects.filter(id__in=product_ids)
        total = 0
        for product in products:
            total += product.price * self.cart[str(product.id)]
        return total

    '''
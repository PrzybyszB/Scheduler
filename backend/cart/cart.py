import json
from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import CartModel, CartItem
from api.models import Premium, Profile
import redis

redis_instance = redis.StrictRedis(host='redis', port=6379, db=0)

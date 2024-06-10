from rest_framework import serializers
from .models import CartModel, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'premium', 'cart', 'quantity', 'total_price']
        read_only_fields = ['total_price']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = CartModel
        fields = ['id', 'user', 'session_key', 'cart_data', 'created_at', 'updated_at', 'items', 'total_price']
        read_only_fields = ['total_price', 'session_key', 'created_at', 'updated_at']
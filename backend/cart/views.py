from .models import CartModel, CartItem
from .serializers import CartSerializer, CartItemSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
#from .cart import CartClass, redis_instance
import json

class APIRoot(APIView):
    def get(self, request, format=None):
        return Response({
            'cart list': '/api/cart/list/',
            'cart create': '/api/cart/create/',
            'cart delete': '/api/cart/items/delete/<int:cart_id>',
            'cart detail': '/api/cart/<int:cart_id>/items/',
            'cart item add': '/api/cart/items/add/',
            'cart item delete': '/api/cart/<int:cart_id>/items/delete/<int:item_id>/',
            # Add next endpoints
        })

class CartsList(generics.ListAPIView):
    queryset = CartModel.objects.all()
    serializer_class = CartSerializer
    permission_classes =[permissions.AllowAny]

class CartCreate(generics.CreateAPIView):
    queryset = CartModel.objects.all()
    serializer_class = CartSerializer
    permission_classes =[permissions.AllowAny]

class CartDetail(generics.RetrieveAPIView):
    queryset = CartModel.objects.all()
    serializer_class = CartSerializer
    permission_classes =[permissions.AllowAny]

class CartItemAdd(generics.CreateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.AllowAny]   

class CartItemDelete(generics.RetrieveDestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.AllowAny]

    def delete(self, request, *args, **kwargs):
        # Download item from cart
        cart_item = self.get_object()
        cart_id = cart_item.cart_id
        item_id = cart_item.id

        serializer = self.get_serializer(cart_item)
        premium_data = serializer.data

        # Delete Item
        self.perform_destroy(cart_item)

        # Download updated cart
        try:
            cart = CartModel.objects.get(id=cart_id)
            cart_serializer = CartSerializer(cart)
            cart_data = cart_serializer.data

            return Response(
                {
                    "message": f"Item with ID {item_id} was deleted from cart {cart_id}",
                    "data": premium_data,
                    "cart": f"Updated cart with ID {cart_id}",
                    "cart_data": cart_data
                },
                status=status.HTTP_200_OK
            )
        except CartModel.DoesNotExist:
            return Response(
                {"message": "Cart not found"},
                status=status.HTTP_404_NOT_FOUND
            )

'''
TAK POWIINNY WYGLĄDAĆ VIEWSY DO TEGO CART.PY sprawdzić to 


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Premium
from .utils import add_to_cart, synchronize_cart_with_db

@login_required
def add_to_cart_view(request, premium_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        add_to_cart(request.user, premium_id, quantity)
        messages.success(request, f"Przedmiot został dodany do koszyka.")
        return redirect('koszyk')

@login_required
def koszyk_view(request):
    synchronize_cart_with_db(request.user)
    cart_items = get_cart_items(request.user)
    total_price = calculate_cart_total(request.user)
    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'koszyk.html', context)


'''
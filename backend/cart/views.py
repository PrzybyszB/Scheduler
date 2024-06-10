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
            'cart delete': '/api/cart/items/delete/<int:pk>',
            'cart detail': '/api/cart/<int:pk>/',
            'cart item add': '/api/cart/items/add/<int:pk>/',
            'cart item delete': '/api/cart/items/delete/<int:pk>',
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
'''
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        premium_data = serializer.data
        premium_id = instance.id
        self.perform_destroy(instance)
        return Response(
            {
                "message": f"Premium with ID {premium_id} was deleted from cart",
                "data": premium_data
            },
            status=status.HTTP_200_OK
        )
'''


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
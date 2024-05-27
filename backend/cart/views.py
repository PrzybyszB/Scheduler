from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView



class APIRoot(APIView):
    def get(self, request, format=None):
        return Response({
            'cart list': '/api/cart/list/',
            'cart create': '/api/cart/create/',
            'cart detail': '/api/cart/<int:pk>/',
            'cart item add': '/api/cart/items/add/<int:pk>/',
            'cart item delete': '/api/cart/items/add/<int:pk>',
            # Add next endpoints
        })



class CartsList(generics.ListAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes =[permissions.AllowAny]


class CartCreate(generics.CreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes =[permissions.AllowAny]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save(session_key=self.request.session.session_key)


class CartDetail(generics.RetrieveAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes =[permissions.AllowAny]



class CartItemAdd(generics.CreateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.AllowAny]
        
    def perform_create(self, serializer):
        pass
    #     cart, created = Cart.objects.get_or_create(
    #        user=self.request.user if self.request.user.is_authenticated else None,
    #        session_key=self.request.session.session_key if not self.request.user.is_authenticated else None
    #    )
    #     serializer.save(cart=cart)

class CartItemDelete(generics.RetrieveDestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.AllowAny]

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

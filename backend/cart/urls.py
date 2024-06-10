from django.urls import path
from .views import CartCreate, CartDetail, CartItemAdd, CartItemDelete, CartsList, APIRoot

urlpatterns = [
    path('', APIRoot.as_view(), name='cart-root'),
    path('list/', CartsList.as_view(), name='carts-list'),
    path('create/', CartCreate.as_view(), name='cart-create'),
    path('<int:pk>/', CartDetail.as_view(), name='cart-detail'),
    path('items/add/', CartItemAdd.as_view(), name='cartitem-add'),
    path('items/delete/<int:pk>/', CartItemDelete.as_view(), name='cartitem-delete'),
]
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('orders/', views.ListOrderView.as_view(), name='orders'),
    path('orders/<int:pk>/', views.DetailOrderView.as_view(), name='order_detail'),
    path('order/confirmation/', views.OrderConfirmationView.as_view(), name='order_confirmation'),
    path('orders/add/', views.AddOrderView.as_view(), name='add_order'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('add_cart_item/<int:pk>/', views.AddCartItemView.as_view(), name='add_cart_item'),
    path('delete_cart_item/<int:pk>/', views.DeleteCartItemView.as_view(), name='delete_cart_item'),
    path('update_cart_item/<int:pk>/', views.UpdateCartItemView.as_view(), name='update_cart_item'),

]

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, DetailView, View, DeleteView, UpdateView, ListView, FormView

from orders.forms import AddressForm
from orders.models import Cart, CartItem, Order, OrderItem, Address
from shop.models import Product
from django.urls import reverse_lazy


class CartView(LoginRequiredMixin, ListView):
    template_name = 'orders/cart.html'
    context_object_name = 'cart_items'
    login_url = reverse_lazy('users:login')

    def get_queryset(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items = self.get_queryset()
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        context['total_amount'] = total_amount

        return context


class AddCartItemView(View):
    @staticmethod
    def get(request, pk):
        add_to_cart = True
        product = get_object_or_404(Product, pk=pk)

        try:
            cart, _ = Cart.objects.get_or_create(user=request.user)

            if product.stock > 0:
                cart_item, cart_item_created = CartItem.objects.get_or_create(cart=cart, product=product)
                if not cart_item_created:
                    cart_item.quantity += 1
                elif cart_item_created:
                    cart_item.quantity = 1

                cart_item.save()
            else:
                add_to_cart = False
        except Exception as e:
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            if add_to_cart:
                messages.success(request, f'{product.name} was added to your cart.')
            else:
                messages.error(request, f'Sorry, {product.name} is out of stock.')

            return redirect(request.META.get('HTTP_REFERER'))


class DeleteCartItemView(DeleteView):
    model = CartItem
    success_url = reverse_lazy('orders:cart')


class UpdateCartItemView(View):
    @staticmethod
    def post(request, pk):
        cart_item = CartItem.objects.get(pk=pk, cart__user=request.user)
        new_quantity = int(request.POST['quantity'])

        if 0 < new_quantity <= cart_item.product.stock:
            cart_item.quantity = new_quantity
            cart_item.save()

        return redirect('orders:cart')


class ListOrderView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('users:login')
    model = Order
    template_name = 'orders/orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class DetailOrderView(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy('users:login')
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_items'] = OrderItem.objects.filter(order=self.object)
        return context


class OrderConfirmationView(LoginRequiredMixin, ListView, FormView):
    login_url = reverse_lazy('users:login')
    template_name = 'orders/order_confirmation.html'
    form_class = AddressForm
    context_object_name = 'cart_items'
    success_url = reverse_lazy('orders:add_order')

    def get_queryset(self):
        cart = Cart.objects.get(user=self.request.user)
        return CartItem.objects.filter(cart=cart)

    def form_valid(self, form):
        address = form.save()
        self.request.session['address_id'] = address.id
        return redirect(self.get_success_url())

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items = self.get_queryset()

        if self.request.method == 'GET':
            context['form'] = self.form_class()

        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        context['total_amount'] = total_amount

        return context


class AddOrderView(LoginRequiredMixin, View):
    login_url = reverse_lazy('users:login')

    @staticmethod
    def get(request):
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items:
            return redirect('orders:cart')

        address_id = request.session.get('address_id')
        if not address_id:
            return redirect('orders:order_confirmation')
        address = get_object_or_404(Address, id=address_id)

        order = Order.objects.create(user=user, order_address=address, total_amount=0)
        total_amount = 0

        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, price=item.product.price,
                                     quantity=item.quantity)
            total_amount += item.product.price * item.quantity

            product = item.product
            product.stock -= item.quantity
            product.save()

            item.delete()

        order.total_amount = total_amount
        order.save()

        del request.session['address_id']

        return redirect('orders:cart')

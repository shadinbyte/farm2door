# orders/views.py

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone

from .models import Cart, CartItem, Order, OrderItem, OrderTracking
from .serializers import (
    CartSerializer, CartItemSerializer, OrderListSerializer,
    OrderDetailSerializer, CreateOrderSerializer, OrderTrackingSerializer
)
from products.models import Product

# Cart Management Views

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_cart(request):
    """Get customer's cart"""
    if request.user.user_type != 'customer':
        return Response({'error': 'Only customers can access cart'},
                       status=status.HTTP_403_FORBIDDEN)

    cart, created = Cart.objects.get_or_create(customer=request.user)
    serializer = CartSerializer(cart)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_to_cart(request):
    """Add item to cart"""
    if request.user.user_type != 'customer':
        return Response({'error': 'Only customers can add to cart'},
                       status=status.HTTP_403_FORBIDDEN)

    cart, created = Cart.objects.get_or_create(customer=request.user)

    serializer = CartItemSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            # Update quantity if item already exists
            cart_item.quantity = quantity
            cart_item.save()

        return Response({
            'message': 'Item added to cart',
            'cart_item': CartItemSerializer(cart_item).data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    if request.user.user_type != 'customer':
        return Response({'error': 'Only customers can update cart'},
                       status=status.HTTP_403_FORBIDDEN)

    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)

    quantity = request.data.get('quantity')
    if not quantity or quantity < 1:
        return Response({'error': 'Quantity must be at least 1'},
                       status=status.HTTP_400_BAD_REQUEST)

    # Validate quantity against stock
    if quantity > cart_item.product.stock_quantity:
        return Response({
            'error': f'Only {cart_item.product.stock_quantity} items available'
        }, status=status.HTTP_400_BAD_REQUEST)

    cart_item.quantity = quantity
    cart_item.save()

    return Response({
        'message': 'Cart item updated',
        'cart_item': CartItemSerializer(cart_item).data
    })

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def clear_cart(request):
    """Clear all items from cart"""
    if request.user.user_type != 'customer':
        return Response({'error': 'Only customers can clear cart'},
                       status=status.HTTP_403_FORBIDDEN)

    try:
        cart = Cart.objects.get(customer=request.user)
        cart.items.all().delete()
        return Response({'message': 'Cart cleared successfully'})
    except Cart.DoesNotExist:
        return Response({'message': 'Cart is already empty'})

# Order Management Views

class CreateOrderView(generics.CreateAPIView):
    """Create new order from cart"""
    serializer_class = CreateOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if request.user.user_type != 'customer':
            return Response({'error': 'Only customers can create orders'},
                           status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()

            # Send order confirmation (we'll implement this later)
            # send_order_confirmation_email.delay(order.id)

            return Response({
                'message': 'Order created successfully',
                'order': OrderDetailSerializer(order).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerOrderListView(generics.ListAPIView):
    """List customer's orders"""
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type != 'customer':
            return Order.objects.none()

        return Order.objects.filter(
            customer=self.request.user
        ).order_by('-created_at')

class CustomerOrderDetailView(generics.RetrieveAPIView):
    """Get customer's order details"""
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'order_number'

    def get_queryset(self):
        if self.request.user.user_type != 'customer':
            return Order.objects.none()

        return Order.objects.filter(customer=self.request.user)

class FarmerOrderListView(generics.ListAPIView):
    """List orders containing farmer's products"""
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type != 'farmer':
            return Order.objects.none()

        farmer_profile = self.request.user.farmer_profile
        return Order.objects.filter(
            items__farmer=farmer_profile
        ).distinct().order_by('-created_at')

class FarmerOrderDetailView(generics.RetrieveAPIView):
    """Get order details for farmer (only items they supply)"""
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'order_number'

    def get_queryset(self):
        if self.request.user.user_type != 'farmer':
            return Order.objects.none()

        farmer_profile = self.request.user.farmer_profile
        return Order.objects.filter(items__farmer=farmer_profile).distinct()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_order_status(request, order_number):
    """Update order status (farmer or admin only)"""
    if request.user.user_type not in ['farmer', 'admin']:
        return Response({'error': 'Permission denied'},
                       status=status.HTTP_403_FORBIDDEN)

    order = get_object_or_404(Order, order_number=order_number)

    # Check if farmer owns products in this order
    if request.user.user_type == 'farmer':
        farmer_profile = request.user.farmer_profile
        if not order.items.filter(farmer=farmer_profile).exists():
            return Response({'error': 'You can only update orders containing your products'},
                           status=status.HTTP_403_FORBIDDEN)

    new_status = request.data.get('status')
    description = request.data.get('description', '')
    location = request.data.get('location', '')
    estimated_time = request.data.get('estimated_time')

    # Validate status transition
    valid_statuses = dict(OrderTracking.TRACKING_STATUS_CHOICES).keys()
    if new_status not in valid_statuses:
        return Response({'error': 'Invalid status'},
                       status=status.HTTP_400_BAD_REQUEST)

    # Create tracking entry
    tracking = OrderTracking.objects.create(
        order=order,
        status=new_status,
        description=description,
        location=location,
        estimated_time=estimated_time,
        updated_by=request.user
    )

    # Update order status based on tracking status
    status_mapping = {
        'order_placed': 'pending',
        'farmer_confirmed': 'confirmed',
        'preparing': 'processing',
        'ready_pickup': 'ready_for_pickup',
        'picked_up': 'picked_up',
        'warehouse': 'in_transit',
        'dispatch': 'in_transit',
        'out_delivery': 'out_for_delivery',
        'delivered': 'delivered',
    }

    if new_status in status_mapping:
        order.status = status_mapping[new_status]
        if new_status == 'delivered':
            order.actual_delivery_date = timezone.now()
        order.save()

    return Response({
        'message': 'Order status updated successfully',
        'tracking': OrderTrackingSerializer(tracking).data
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_order(request, order_number):
    """Cancel order (customer only, if not yet processed)"""
    if request.user.user_type != 'customer':
        return Response({'error': 'Only customers can cancel orders'},
                       status=status.HTTP_403_FORBIDDEN)

    order = get_object_or_404(Order, order_number=order_number, customer=request.user)

    # Check if order can be cancelled
    if order.status not in ['pending', 'confirmed']:
        return Response({'error': 'Order cannot be cancelled at this stage'},
                       status=status.HTTP_400_BAD_REQUEST)

    # Restore product stock
    for item in order.items.all():
        product = item.product
        product.stock_quantity += item.quantity
        product.total_sold -= item.quantity
        product.save()

    # Update order status
    order.status = 'cancelled'
    order.save()

    # Add tracking entry
    OrderTracking.objects.create(
        order=order,
        status='order_placed',  # We don't have cancel status in tracking choices
        description='Order cancelled by customer',
        updated_by=request.user
    )

    return Response({'message': 'Order cancelled successfully'})

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_orders(request):
    """Get all orders for admin"""
    orders = Order.objects.all().order_by('-created_at')

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    # Filter by payment status if provided
    payment_status_filter = request.GET.get('payment_status')
    if payment_status_filter:
        orders = orders.filter(payment_status=payment_status_filter)

    serializer = OrderListSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def order_statuses(request):
    """Get available order statuses"""
    return Response({
        'order_statuses': dict(Order.ORDER_STATUS_CHOICES),
        'tracking_statuses': dict(OrderTracking.TRACKING_STATUS_CHOICES),
        'payment_statuses': dict(Order.PAYMENT_STATUS_CHOICES)
    })'])
@permission_classes([permissions.IsAuthenticated])
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    if request.user.user_type != 'customer':
        return Response({'error': 'Only customers can modify cart'},
                       status=status.HTTP_403_FORBIDDEN)

    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
    cart_item.delete()

    return Response({'message': 'Item removed from cart'})

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    if request.user.user_type != 'customer':
        return Response({'error': 'Only customers can modify cart'},
                       status=status.HTTP_403_FORBIDDEN)

    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
    cart_item.delete()

    return Response({'message': 'Item removed from cart'})

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_order(request, order_number):
    """Delete order (admin only)"""
    if request.user.user_type != 'admin':
        return Response({'error': 'Only admins can delete orders'},
                       status=status.HTTP_403_FORBIDDEN)

    order = get_object_or_404(Order, order_number=order_number)

    # Ensure order is not already delivered or processed
    if order.status == 'delivered':
        return Response({'error': 'Delivered orders cannot be deleted'},
                       status=status.HTTP_400_BAD_REQUEST)

    # Cancel the order if it's not processed
    if order.status not in ['pending', 'confirmed']:
        return Response({'error': 'Order cannot be deleted at this stage'},
                       status=status.HTTP_400_BAD_REQUEST)

    # Restore product stock before deletion
    for item in order.items.all():
        product = item.product
        product.stock_quantity += item.quantity
        product.total_sold -= item.quantity
        product.save()

    order.delete()

    return Response({'message': 'Order deleted successfully'})

# View to retrieve all available order statuses
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def order_statuses(request):
    """Get available order statuses"""
    return Response({
        'order_statuses': dict(Order.ORDER_STATUS_CHOICES),
        'tracking_statuses': dict(OrderTracking.TRACKING_STATUS_CHOICES),
        'payment_statuses': dict(Order.PAYMENT_STATUS_CHOICES)
    })


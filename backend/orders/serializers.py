# orders/serializers.py

from decimal import Decimal

from accounts.serializers import FarmerProfileSerializer
from products.serializers import ProductListSerializer
from rest_framework import serializers

from .models import Cart, CartItem, Order, OrderItem, OrderPayment, OrderTracking


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity", "subtotal", "created_at"]
        read_only_fields = ["cart"]

    def validate(self, attrs):
        product_id = attrs.get("product_id")
        quantity = attrs.get("quantity")

        try:
            from products.models import Product

            product = Product.objects.get(id=product_id, is_available=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or not available")

        # Check stock
        if quantity > product.stock_quantity:
            raise serializers.ValidationError(
                f"Only {product.stock_quantity} items available"
            )

        # Check minimum/maximum order quantities
        if quantity < product.minimum_order_quantity:
            raise serializers.ValidationError(
                f"Minimum order quantity is {product.minimum_order_quantity}"
            )

        if product.maximum_order_quantity and quantity > product.maximum_order_quantity:
            raise serializers.ValidationError(
                f"Maximum order quantity is {product.maximum_order_quantity}"
            )

        attrs["product"] = product
        return attrs


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "items",
            "total_items",
            "total_amount",
            "created_at",
            "updated_at",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    product_details = ProductListSerializer(source="product", read_only=True)
    farmer_name = serializers.CharField(source="farmer.farm_name", read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_details",
            "farmer_name",
            "quantity",
            "unit_price",
            "subtotal",
            "product_name",
            "product_unit",
        ]


class OrderTrackingSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    updated_by_name = serializers.CharField(
        source="updated_by.username", read_only=True
    )

    class Meta:
        model = OrderTracking
        fields = [
            "id",
            "status",
            "status_display",
            "description",
            "location",
            "estimated_time",
            "actual_time",
            "updated_by_name",
        ]


class OrderPaymentSerializer(serializers.ModelSerializer):
    payment_method_display = serializers.CharField(
        source="get_payment_method_display", read_only=True
    )

    class Meta:
        model = OrderPayment
        fields = [
            "id",
            "payment_method",
            "payment_method_display",
            "amount",
            "transaction_id",
            "is_successful",
            "created_at",
        ]
        read_only_fields = ["transaction_id", "is_successful"]


class OrderListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    payment_status_display = serializers.CharField(
        source="get_payment_status_display", read_only=True
    )
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "status",
            "status_display",
            "payment_status",
            "payment_status_display",
            "total_amount",
            "items_count",
            "estimated_delivery_date",
            "created_at",
        ]

    def get_items_count(self, obj):
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    tracking = OrderTrackingSerializer(many=True, read_only=True)
    payment = OrderPaymentSerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    payment_status_display = serializers.CharField(
        source="get_payment_status_display", read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "status",
            "status_display",
            "payment_status",
            "payment_status_display",
            "subtotal",
            "delivery_fee",
            "tax_amount",
            "discount_amount",
            "total_amount",
            "delivery_address",
            "delivery_city",
            "delivery_postal_code",
            "delivery_phone",
            "delivery_instructions",
            "estimated_delivery_date",
            "actual_delivery_date",
            "customer_notes",
            "items",
            "tracking",
            "payment",
            "created_at",
            "updated_at",
        ]


class CreateOrderSerializer(serializers.Serializer):
    delivery_address = serializers.CharField(max_length=500)
    delivery_city = serializers.CharField(max_length=100)
    delivery_postal_code = serializers.CharField(max_length=20)
    delivery_phone = serializers.CharField(max_length=17)
    delivery_instructions = serializers.CharField(
        max_length=500, required=False, allow_blank=True
    )
    payment_method = serializers.ChoiceField(
        choices=OrderPayment.PAYMENT_METHOD_CHOICES
    )
    customer_notes = serializers.CharField(
        max_length=500, required=False, allow_blank=True
    )

    def validate(self, attrs):
        # Get customer's cart
        user = self.context["request"].user
        try:
            cart = Cart.objects.get(customer=user)
        except Cart.DoesNotExist:
            raise serializers.ValidationError("Cart is empty")

        if not cart.items.exists():
            raise serializers.ValidationError("Cart is empty")

        # Validate all cart items are still available
        for item in cart.items.all():
            if not item.product.is_available:
                raise serializers.ValidationError(
                    f"Product {item.product.name} is no longer available"
                )

            if item.quantity > item.product.stock_quantity:
                raise serializers.ValidationError(
                    f"Only {item.product.stock_quantity} units of {item.product.name} available"
                )

        attrs["cart"] = cart
        return attrs

    def create(self, validated_data):
        cart = validated_data.pop("cart")
        user = self.context["request"].user

        # Calculate totals
        subtotal = cart.total_amount
        delivery_fee = Decimal("50.00")  # Fixed delivery fee for now
        tax_amount = subtotal * Decimal("0.05")  # 5% tax
        total_amount = subtotal + delivery_fee + tax_amount

        # Create order
        order = Order.objects.create(
            customer=user,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            tax_amount=tax_amount,
            total_amount=total_amount,
            **validated_data,
        )

        # Create order items and update product stock
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                farmer=cart_item.product.farmer,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price_per_unit,
                subtotal=cart_item.subtotal,
            )

            # Update product stock
            product = cart_item.product
            product.stock_quantity -= cart_item.quantity
            product.total_sold += cart_item.quantity
            product.save()

        # Create initial tracking
        OrderTracking.objects.create(
            order=order,
            status="order_placed",
            description="Order has been placed successfully",
            updated_by=user,
        )

        # Clear cart
        cart.items.all().delete()

        return order

# orders/models.py

from decimal import Decimal

from accounts.models import User
from django.core.validators import MinValueValidator
from django.db import models
from products.models import Product


class Cart(models.Model):
    customer = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": "customer"},
        related_name="cart",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.customer.username}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["cart", "product"]

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        return self.quantity * self.product.price_per_unit

    def clean(self):
        from django.core.exceptions import ValidationError

        # Check if product is available
        if not self.product.is_available:
            raise ValidationError("Product is not available")

        # Check stock quantity
        if self.quantity > self.product.stock_quantity:
            raise ValidationError(f"Only {self.product.stock_quantity} items available")

        # Check minimum and maximum order quantities
        if self.quantity < self.product.minimum_order_quantity:
            raise ValidationError(
                f"Minimum order quantity is {self.product.minimum_order_quantity}"
            )

        if (
            self.product.maximum_order_quantity
            and self.quantity > self.product.maximum_order_quantity
        ):
            raise ValidationError(
                f"Maximum order quantity is {self.product.maximum_order_quantity}"
            )


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("ready_for_pickup", "Ready for Pickup"),
        ("picked_up", "Picked Up"),
        ("in_transit", "In Transit"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    # Order identification
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": "customer"},
        related_name="orders",
    )

    # Order details
    status = models.CharField(
        max_length=20, choices=ORDER_STATUS_CHOICES, default="pending"
    )
    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS_CHOICES, default="pending"
    )

    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Delivery information
    delivery_address = models.TextField()
    delivery_city = models.CharField(max_length=100)
    delivery_postal_code = models.CharField(max_length=20)
    delivery_latitude = models.DecimalField(
        max_digits=22, decimal_places=16, blank=True, null=True
    )
    delivery_longitude = models.DecimalField(
        max_digits=22, decimal_places=16, blank=True, null=True
    )

    # Contact information
    delivery_phone = models.CharField(max_length=17)
    delivery_instructions = models.TextField(blank=True)

    # Timing
    estimated_delivery_date = models.DateTimeField(blank=True, null=True)
    actual_delivery_date = models.DateTimeField(blank=True, null=True)

    # Notes
    customer_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["customer", "status"]),
            models.Index(fields=["order_number"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Order {self.order_number} - {self.customer.username}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        import uuid

        return f"ORD{uuid.uuid4().hex[:8].upper()}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    farmer = models.ForeignKey("accounts.FarmerProfile", on_delete=models.CASCADE)

    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    # Product details at time of order (for record keeping)
    product_name = models.CharField(max_length=200)
    product_unit = models.CharField(max_length=10)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.quantity} x {self.product_name} in Order {self.order.order_number}"
        )

    def save(self, *args, **kwargs):
        # Auto-calculate subtotal
        self.subtotal = self.quantity * self.unit_price

        # Store product details
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_unit:
            self.product_unit = self.product.unit

        super().save(*args, **kwargs)


class OrderTracking(models.Model):
    TRACKING_STATUS_CHOICES = [
        ("order_placed", "Order Placed"),
        ("farmer_confirmed", "Farmer Confirmed"),
        ("preparing", "Preparing Order"),
        ("ready_pickup", "Ready for Pickup"),
        ("picked_up", "Picked Up from Farm"),
        ("warehouse", "At Processing Center"),
        ("dispatch", "Dispatched for Delivery"),
        ("out_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tracking")
    status = models.CharField(max_length=20, choices=TRACKING_STATUS_CHOICES)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    estimated_time = models.DateTimeField(blank=True, null=True)
    actual_time = models.DateTimeField(auto_now_add=True)

    # Staff who updated the status
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["-actual_time"]

    def __str__(self):
        return f"Order {self.order.order_number} - {self.get_status_display()}"


class OrderPayment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("card", "Credit/Debit Card"),
        ("mobile_banking", "Mobile Banking"),
        ("bank_transfer", "Bank Transfer"),
        ("cash_on_delivery", "Cash on Delivery"),
    ]

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="payment"
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Payment gateway details
    transaction_id = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(blank=True, null=True)

    # Status tracking
    is_successful = models.BooleanField(default=False)
    failure_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Order {self.order.order_number}"

# delivery/models.py

from accounts.models import User
from django.core.validators import RegexValidator
from django.db import models
from orders.models import Order


class DeliveryZone(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Geographic boundaries
    postal_codes = models.TextField(help_text="Comma-separated postal codes")
    cities = models.TextField(help_text="Comma-separated city names")

    # Delivery settings
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2)
    estimated_delivery_hours = models.IntegerField(
        help_text="Estimated delivery time in hours"
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DeliveryPartner(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number must be entered in the format: '+999999999'.",
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    email = models.EmailField()

    # Service areas
    service_zones = models.ManyToManyField(
        DeliveryZone, related_name="delivery_partners"
    )

    # Business details
    business_license = models.CharField(max_length=100, blank=True)
    vehicle_types = models.CharField(
        max_length=200, help_text="Types of vehicles available"
    )

    # Performance metrics
    average_delivery_time = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )  # in hours
    success_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=100
    )  # percentage
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DeliveryAssignment(models.Model):
    ASSIGNMENT_STATUS_CHOICES = [
        ("assigned", "Assigned"),
        ("accepted", "Accepted"),
        ("picked_up", "Picked Up"),
        ("in_transit", "In Transit"),
        ("delivered", "Delivered"),
        ("failed", "Failed Delivery"),
        ("returned", "Returned to Sender"),
    ]

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="delivery_assignment"
    )
    delivery_partner = models.ForeignKey(
        DeliveryPartner, on_delete=models.CASCADE, related_name="assignments"
    )
    delivery_zone = models.ForeignKey(DeliveryZone, on_delete=models.CASCADE)

    # Assignment details
    status = models.CharField(
        max_length=20, choices=ASSIGNMENT_STATUS_CHOICES, default="assigned"
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    # Delivery person details
    delivery_person_name = models.CharField(max_length=100, blank=True)
    delivery_person_phone = models.CharField(max_length=17, blank=True)

    # Delivery tracking details
    pickup_location = models.CharField(max_length=200, blank=True)
    current_location = models.CharField(max_length=200, blank=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    actual_delivery_time = models.DateTimeField(null=True, blank=True)

    # Delivery notes and updates
    pickup_notes = models.TextField(blank=True)
    delivery_notes = models.TextField(blank=True)
    customer_feedback = models.TextField(blank=True)

    # Performance tracking
    delivery_rating = models.IntegerField(
        null=True, blank=True, help_text="1-5 rating from customer"
    )
    delivery_issues = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Delivery Assignment - Order {self.order.order_number} ({self.status})"

    @property
    def is_completed(self):
        return self.status == "delivered"

    @property
    def delivery_duration(self):
        """Calculate delivery duration in hours"""
        if self.picked_up_at and self.delivered_at:
            duration = self.delivered_at - self.picked_up_at
            return duration.total_seconds() / 3600
        return None


class DeliveryTracking(models.Model):
    """Detailed tracking events for deliveries"""

    TRACKING_EVENT_CHOICES = [
        ("order_confirmed", "Order Confirmed"),
        ("assigned_partner", "Assigned to Delivery Partner"),
        ("partner_accepted", "Partner Accepted Delivery"),
        ("pickup_scheduled", "Pickup Scheduled"),
        ("picked_up_from_farm", "Picked Up from Farm"),
        ("at_sorting_center", "At Sorting Center"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivery_attempted", "Delivery Attempted"),
        ("delivered_successfully", "Delivered Successfully"),
        ("delivery_failed", "Delivery Failed"),
        ("returned_to_sender", "Returned to Sender"),
    ]

    delivery_assignment = models.ForeignKey(
        DeliveryAssignment, on_delete=models.CASCADE, related_name="tracking_events"
    )
    event = models.CharField(max_length=30, choices=TRACKING_EVENT_CHOICES)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)

    # Location coordinates
    latitude = models.DecimalField(
        max_digits=22, decimal_places=16, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=22, decimal_places=16, blank=True, null=True
    )

    # Timing
    estimated_time = models.DateTimeField(blank=True, null=True)
    actual_time = models.DateTimeField(auto_now_add=True)

    # Staff who created the update
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Additional data
    metadata = models.JSONField(
        blank=True, null=True, help_text="Additional tracking data"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["delivery_assignment", "event"]),
            models.Index(fields=["actual_time"]),
        ]

    def __str__(self):
        return f"{self.get_event_display()} - {self.delivery_assignment.order.order_number}"


class DeliveryRoute(models.Model):
    """Optimized delivery routes for efficiency"""

    name = models.CharField(max_length=100)
    delivery_partner = models.ForeignKey(
        DeliveryPartner, on_delete=models.CASCADE, related_name="routes"
    )
    delivery_zone = models.ForeignKey(DeliveryZone, on_delete=models.CASCADE)

    # Route details
    start_location = models.CharField(max_length=200)
    route_sequence = models.JSONField(help_text="Ordered list of delivery stops")
    estimated_duration = models.IntegerField(help_text="Estimated duration in minutes")

    # Route optimization
    total_distance = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )
    fuel_cost = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )

    # Status
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Route {self.name} - {self.delivery_partner.name}"


class DeliverySlot(models.Model):
    """Time slots for delivery scheduling"""

    SLOT_TYPE_CHOICES = [
        ("morning", "Morning (8AM - 12PM)"),
        ("afternoon", "Afternoon (12PM - 6PM)"),
        ("evening", "Evening (6PM - 8PM)"),
    ]

    delivery_zone = models.ForeignKey(
        DeliveryZone, on_delete=models.CASCADE, related_name="delivery_slots"
    )
    slot_type = models.CharField(max_length=20, choices=SLOT_TYPE_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    # Capacity management
    max_deliveries = models.IntegerField(default=10)
    current_bookings = models.IntegerField(default=0)

    # Pricing
    additional_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    # Availability
    available_days = models.JSONField(
        default=list, help_text="List of available days (0=Monday, 6=Sunday)"
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["delivery_zone", "slot_type", "start_time"]

    def __str__(self):
        return f"{self.delivery_zone.name} - {self.get_slot_type_display()}"

    @property
    def is_available(self):
        return self.current_bookings < self.max_deliveries and self.is_active

    def book_slot(self):
        """Book a delivery slot"""
        if self.is_available:
            self.current_bookings += 1
            self.save()
            return True
        return False

    def release_slot(self):
        """Release a booked slot"""
        if self.current_bookings > 0:
            self.current_bookings -= 1
            self.save()


class DeliveryFeedback(models.Model):
    """Customer feedback on delivery experience"""

    RATING_CHOICES = [
        (1, "Very Poor"),
        (2, "Poor"),
        (3, "Average"),
        (4, "Good"),
        (5, "Excellent"),
    ]

    delivery_assignment = models.OneToOneField(
        DeliveryAssignment, on_delete=models.CASCADE, related_name="feedback"
    )
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={"user_type": "customer"}
    )

    # Ratings
    overall_rating = models.IntegerField(choices=RATING_CHOICES)
    delivery_time_rating = models.IntegerField(choices=RATING_CHOICES)
    delivery_person_rating = models.IntegerField(choices=RATING_CHOICES)
    product_condition_rating = models.IntegerField(choices=RATING_CHOICES)

    # Feedback
    positive_feedback = models.TextField(blank=True)
    improvement_suggestions = models.TextField(blank=True)

    # Additional questions
    would_recommend = models.BooleanField(null=True)
    delivery_issues = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback - Order {self.delivery_assignment.order.order_number} ({self.overall_rating}★)"

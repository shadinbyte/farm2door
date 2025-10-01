# delivery/serializers.py

from django.utils import timezone
from orders.serializers import OrderListSerializer
from rest_framework import serializers

from .models import (
    DeliveryAssignment,
    DeliveryFeedback,
    DeliveryPartner,
    DeliveryRoute,
    DeliverySlot,
    DeliveryTracking,
    DeliveryZone,
)


class DeliveryZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryZone
        fields = [
            "id",
            "name",
            "description",
            "delivery_fee",
            "estimated_delivery_hours",
            "is_active",
        ]


class DeliveryPartnerSerializer(serializers.ModelSerializer):
    service_zone_names = serializers.StringRelatedField(
        source="service_zones", many=True, read_only=True
    )

    class Meta:
        model = DeliveryPartner
        fields = [
            "id",
            "name",
            "contact_person",
            "phone_number",
            "email",
            "vehicle_types",
            "average_delivery_time",
            "success_rate",
            "rating",
            "is_active",
            "service_zone_names",
        ]


class DeliveryTrackingSerializer(serializers.ModelSerializer):
    event_display = serializers.CharField(source="get_event_display", read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True
    )
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryTracking
        fields = [
            "id",
            "event",
            "event_display",
            "description",
            "location",
            "latitude",
            "longitude",
            "estimated_time",
            "actual_time",
            "created_by_name",
            "time_ago",
            "metadata",
        ]

    def get_time_ago(self, obj):
        """Calculate time ago from actual time"""
        now = timezone.now()
        diff = now - obj.actual_time

        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            return "Just now"


class DeliveryAssignmentListSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source="order.order_number", read_only=True)
    customer_name = serializers.CharField(
        source="order.customer.get_full_name", read_only=True
    )
    delivery_partner_name = serializers.CharField(
        source="delivery_partner.name", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    is_completed = serializers.ReadOnlyField()

    class Meta:
        model = DeliveryAssignment
        fields = [
            "id",
            "order_number",
            "customer_name",
            "delivery_partner_name",
            "status",
            "status_display",
            "assigned_at",
            "estimated_delivery_time",
            "is_completed",
        ]


class DeliveryAssignmentDetailSerializer(serializers.ModelSerializer):
    order = OrderListSerializer(read_only=True)
    delivery_partner = DeliveryPartnerSerializer(read_only=True)
    delivery_zone = DeliveryZoneSerializer(read_only=True)
    tracking_events = DeliveryTrackingSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    is_completed = serializers.ReadOnlyField()
    delivery_duration = serializers.ReadOnlyField()

    class Meta:
        model = DeliveryAssignment
        fields = [
            "id",
            "order",
            "delivery_partner",
            "delivery_zone",
            "status",
            "status_display",
            "assigned_at",
            "accepted_at",
            "picked_up_at",
            "delivered_at",
            "delivery_person_name",
            "delivery_person_phone",
            "pickup_location",
            "current_location",
            "estimated_delivery_time",
            "actual_delivery_time",
            "pickup_notes",
            "delivery_notes",
            "delivery_rating",
            "delivery_issues",
            "tracking_events",
            "is_completed",
            "delivery_duration",
        ]


class CreateDeliveryTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryTracking
        fields = [
            "delivery_assignment",
            "event",
            "description",
            "location",
            "latitude",
            "longitude",
            "estimated_time",
            "metadata",
        ]

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        tracking = DeliveryTracking.objects.create(**validated_data)

        # Update delivery assignment status based on tracking event
        self.update_delivery_status(tracking)

        return tracking

    def update_delivery_status(self, tracking):
        """Update delivery assignment status based on tracking event"""
        assignment = tracking.delivery_assignment
        event = tracking.event

        status_mapping = {
            "assigned_partner": "assigned",
            "partner_accepted": "accepted",
            "picked_up_from_farm": "picked_up",
            "out_for_delivery": "in_transit",
            "delivered_successfully": "delivered",
            "delivery_failed": "failed",
            "returned_to_sender": "returned",
        }

        if event in status_mapping:
            assignment.status = status_mapping[event]

            # Update timestamps based on status
            if event == "partner_accepted":
                assignment.accepted_at = timezone.now()
            elif event == "picked_up_from_farm":
                assignment.picked_up_at = timezone.now()
            elif event == "delivered_successfully":
                assignment.delivered_at = timezone.now()
                assignment.actual_delivery_time = timezone.now()

            assignment.save()


class DeliverySlotSerializer(serializers.ModelSerializer):
    slot_type_display = serializers.CharField(
        source="get_slot_type_display", read_only=True
    )
    is_available = serializers.ReadOnlyField()
    availability_percentage = serializers.SerializerMethodField()

    class Meta:
        model = DeliverySlot
        fields = [
            "id",
            "slot_type",
            "slot_type_display",
            "start_time",
            "end_time",
            "max_deliveries",
            "current_bookings",
            "additional_fee",
            "is_available",
            "availability_percentage",
        ]

    def get_availability_percentage(self, obj):
        if obj.max_deliveries > 0:
            return (
                (obj.max_deliveries - obj.current_bookings) / obj.max_deliveries
            ) * 100
        return 0


class DeliveryFeedbackSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.get_full_name", read_only=True
    )
    order_number = serializers.CharField(
        source="delivery_assignment.order.order_number", read_only=True
    )
    overall_rating_display = serializers.CharField(
        source="get_overall_rating_display", read_only=True
    )

    class Meta:
        model = DeliveryFeedback
        fields = [
            "id",
            "customer_name",
            "order_number",
            "overall_rating",
            "overall_rating_display",
            "delivery_time_rating",
            "delivery_person_rating",
            "product_condition_rating",
            "positive_feedback",
            "improvement_suggestions",
            "would_recommend",
            "delivery_issues",
            "created_at",
        ]
        read_only_fields = ["customer", "delivery_assignment"]


class CreateDeliveryFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryFeedback
        fields = [
            "delivery_assignment",
            "overall_rating",
            "delivery_time_rating",
            "delivery_person_rating",
            "product_condition_rating",
            "positive_feedback",
            "improvement_suggestions",
            "would_recommend",
            "delivery_issues",
        ]

    def validate_delivery_assignment(self, value):
        # Ensure customer can only provide feedback for their own deliveries
        user = self.context["request"].user
        if value.order.customer != user:
            raise serializers.ValidationError(
                "You can only provide feedback for your own orders"
            )

        # Ensure delivery is completed
        if value.status != "delivered":
            raise serializers.ValidationError(
                "Feedback can only be provided for completed deliveries"
            )

        # Check if feedback already exists
        if hasattr(value, "feedback"):
            raise serializers.ValidationError(
                "Feedback has already been provided for this delivery"
            )

        return value

    def create(self, validated_data):
        validated_data["customer"] = self.context["request"].user
        return DeliveryFeedback.objects.create(**validated_data)


class DeliveryRouteSerializer(serializers.ModelSerializer):
    delivery_partner_name = serializers.CharField(
        source="delivery_partner.name", read_only=True
    )
    delivery_zone_name = serializers.CharField(
        source="delivery_zone.name", read_only=True
    )

    class Meta:
        model = DeliveryRoute
        fields = [
            "id",
            "name",
            "delivery_partner_name",
            "delivery_zone_name",
            "start_location",
            "route_sequence",
            "estimated_duration",
            "total_distance",
            "fuel_cost",
            "is_active",
        ]


class DeliveryStatsSerializer(serializers.Serializer):
    """Serializer for delivery statistics"""

    total_deliveries = serializers.IntegerField()
    completed_deliveries = serializers.IntegerField()
    pending_deliveries = serializers.IntegerField()
    failed_deliveries = serializers.IntegerField()
    average_delivery_time = serializers.DecimalField(max_digits=5, decimal_places=2)
    success_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    customer_satisfaction = serializers.DecimalField(max_digits=3, decimal_places=2)

    # Zone-wise stats
    zone_stats = serializers.JSONField()

    # Partner performance
    partner_performance = serializers.JSONField()

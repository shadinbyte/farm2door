# delivery/views.py

from datetime import timedelta

from django.db.models import Avg, Count, F, Q, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from orders.models import Order
from rest_framework import filters, generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import (
    DeliveryAssignment,
    DeliveryFeedback,
    DeliveryPartner,
    DeliverySlot,
    DeliveryTracking,
    DeliveryZone,
)
from .serializers import (
    CreateDeliveryFeedbackSerializer,
    CreateDeliveryTrackingSerializer,
    DeliveryAssignmentDetailSerializer,
    DeliveryAssignmentListSerializer,
    DeliveryFeedbackSerializer,
    DeliveryPartnerSerializer,
    DeliverySlotSerializer,
    DeliveryStatsSerializer,
    DeliveryTrackingSerializer,
    DeliveryZoneSerializer,
)

# Public Delivery Information


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def delivery_zones(request):
    """Get all active delivery zones"""
    zones = DeliveryZone.objects.filter(is_active=True)
    serializer = DeliveryZoneSerializer(zones, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def delivery_slots(request):
    """Get available delivery slots for a zone"""
    zone_id = request.GET.get("zone_id")
    if not zone_id:
        return Response(
            {"error": "zone_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    slots = DeliverySlot.objects.filter(delivery_zone_id=zone_id, is_active=True)
    serializer = DeliverySlotSerializer(slots, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def estimate_delivery_time(request):
    """Estimate delivery time for a location"""
    postal_code = request.GET.get("postal_code")
    city = request.GET.get("city")

    if not postal_code or not city:
        return Response(
            {"error": "postal_code and city are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Find matching delivery zone
    zone = DeliveryZone.objects.filter(
        Q(postal_codes__icontains=postal_code) | Q(cities__icontains=city),
        is_active=True,
    ).first()

    if zone:
        # Calculate estimated delivery time
        estimated_time = timezone.now() + timedelta(hours=zone.estimated_delivery_hours)

        return Response(
            {
                "zone": DeliveryZoneSerializer(zone).data,
                "estimated_delivery_time": estimated_time,
                "delivery_fee": zone.delivery_fee,
                "available_slots": DeliverySlotSerializer(
                    zone.delivery_slots.filter(is_active=True), many=True
                ).data,
            }
        )
    else:
        return Response(
            {
                "error": "Delivery not available in this area",
                "message": "We currently do not deliver to this location",
            },
            status=status.HTTP_404_NOT_FOUND,
        )


# Customer Delivery Tracking


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def track_delivery(request, order_number):
    """Track delivery for a specific order"""
    if request.user.user_type != "customer":
        return Response(
            {"error": "Only customers can track deliveries"},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        order = Order.objects.get(order_number=order_number, customer=request.user)
        delivery_assignment = DeliveryAssignment.objects.get(order=order)

        serializer = DeliveryAssignmentDetailSerializer(delivery_assignment)
        return Response(serializer.data)

    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    except DeliveryAssignment.DoesNotExist:
        return Response(
            {
                "error": "Delivery not assigned yet",
                "message": "Your order is being processed and will be assigned for delivery soon",
            },
            status=status.HTTP_404_NOT_FOUND,
        )


class CustomerDeliveryHistoryView(generics.ListAPIView):
    """List customer's delivery history"""

    serializer_class = DeliveryAssignmentListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["assigned_at", "delivered_at"]
    ordering = ["-assigned_at"]

    def get_queryset(self):
        if self.request.user.user_type != "customer":
            return DeliveryAssignment.objects.none()

        return DeliveryAssignment.objects.filter(
            order__customer=self.request.user
        ).select_related("order", "delivery_partner", "delivery_zone")


# Delivery Partner Views


class PartnerDeliveryListView(generics.ListAPIView):
    """List deliveries assigned to a partner"""

    serializer_class = DeliveryAssignmentListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["assigned_at", "estimated_delivery_time"]
    ordering = ["estimated_delivery_time"]

    def get_queryset(self):
        # For now, allow admin users to view partner deliveries
        # In production, you'd have partner-specific authentication
        if not self.request.user.is_staff:
            return DeliveryAssignment.objects.none()

        partner_id = self.request.GET.get("partner_id")
        queryset = DeliveryAssignment.objects.select_related(
            "order", "delivery_partner", "delivery_zone"
        )

        if partner_id:
            queryset = queryset.filter(delivery_partner_id=partner_id)

        # Filter by status
        status_filter = self.request.GET.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def update_delivery_status(request, assignment_id):
    """Update delivery status and add tracking event"""
    if not request.user.is_staff:
        return Response(
            {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
        )

    assignment = get_object_or_404(DeliveryAssignment, id=assignment_id)

    # Validate coordinates if provided
    latitude = request.data.get("latitude")
    longitude = request.data.get("longitude")

    if latitude is not None:
        try:
            latitude = float(latitude)
            if not (-90 <= latitude <= 90):
                return Response(
                    {"error": "Latitude must be between -90 and 90"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid latitude value"}, status=status.HTTP_400_BAD_REQUEST
            )

    if longitude is not None:
        try:
            longitude = float(longitude)
            if not (-180 <= longitude <= 180):
                return Response(
                    {"error": "Longitude must be between -180 and 180"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid longitude value"}, status=status.HTTP_400_BAD_REQUEST
            )

    # Prepare tracking data
    tracking_data = {
        "delivery_assignment": assignment.id,
        "event": request.data.get("event"),
        "description": request.data.get("description", ""),
        "location": request.data.get("location", ""),
        "latitude": latitude,
        "longitude": longitude,
        "metadata": request.data.get("metadata", {}),
    }

    serializer = CreateDeliveryTrackingSerializer(
        data=tracking_data, context={"request": request}
    )

    if serializer.is_valid():
        tracking = serializer.save()

        # Return updated assignment details
        assignment.refresh_from_db()
        response_serializer = DeliveryAssignmentDetailSerializer(assignment)

        return Response(
            {
                "message": "Delivery status updated successfully",
                "tracking_event": DeliveryTrackingSerializer(tracking).data,
                "delivery_assignment": response_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delivery Feedback


class DeliveryFeedbackCreateView(generics.CreateAPIView):
    """Submit delivery feedback"""

    serializer_class = CreateDeliveryFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.user_type != "customer":
            raise PermissionDenied("Only customers can provide feedback")

        feedback = serializer.save()

        # Update delivery assignment rating
        assignment = feedback.delivery_assignment
        assignment.delivery_rating = feedback.overall_rating
        assignment.save()

        # Update delivery partner average rating
        partner = assignment.delivery_partner
        partner_avg = DeliveryFeedback.objects.filter(
            delivery_assignment__delivery_partner=partner
        ).aggregate(Avg("overall_rating"))["overall_rating__avg"]

        if partner_avg:
            partner.rating = round(partner_avg, 2)
            partner.save()


class DeliveryFeedbackListView(generics.ListAPIView):
    """List delivery feedback (admin only)"""

    serializer_class = DeliveryFeedbackSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.OrderingFilter]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = DeliveryFeedback.objects.select_related(
            "customer",
            "delivery_assignment__order",
            "delivery_assignment__delivery_partner",
        )

        # Filter by rating
        min_rating = self.request.GET.get("min_rating")
        if min_rating:
            queryset = queryset.filter(overall_rating__gte=min_rating)

        # Filter by partner
        partner_id = self.request.GET.get("partner_id")
        if partner_id:
            queryset = queryset.filter(
                delivery_assignment__delivery_partner_id=partner_id
            )

        return queryset


# Admin Views


@api_view(["POST"])
@permission_classes([permissions.IsAdminUser])
def assign_delivery(request, order_id):
    """Assign order to delivery partner"""
    order = get_object_or_404(Order, id=order_id)

    # Check if already assigned
    if hasattr(order, "delivery_assignment"):
        return Response(
            {"error": "Order already assigned for delivery"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    partner_id = request.data.get("delivery_partner_id")
    zone_id = request.data.get("delivery_zone_id")

    if not partner_id or not zone_id:
        return Response(
            {"error": "delivery_partner_id and delivery_zone_id are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    partner = get_object_or_404(DeliveryPartner, id=partner_id, is_active=True)
    zone = get_object_or_404(DeliveryZone, id=zone_id, is_active=True)

    # Calculate estimated delivery time if not provided
    estimated_time = request.data.get("estimated_delivery_time")
    if not estimated_time:
        estimated_time = timezone.now() + timedelta(hours=zone.estimated_delivery_hours)

    # Create delivery assignment
    assignment = DeliveryAssignment.objects.create(
        order=order,
        delivery_partner=partner,
        delivery_zone=zone,
        status="assigned",
        delivery_person_name=request.data.get("delivery_person_name", ""),
        delivery_person_phone=request.data.get("delivery_person_phone", ""),
        pickup_location=request.data.get("pickup_location", ""),
        estimated_delivery_time=estimated_time,
    )

    # Create initial tracking event
    DeliveryTracking.objects.create(
        delivery_assignment=assignment,
        event="assigned_partner",
        description=f"Order assigned to {partner.name}",
        created_by=request.user,
    )

    # Update order status
    order.status = "ready_for_pickup"
    order.save()

    serializer = DeliveryAssignmentDetailSerializer(assignment)
    return Response(
        {
            "message": "Delivery assigned successfully",
            "delivery_assignment": serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def delivery_statistics(request):
    """Get delivery statistics"""
    # Date range filtering
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    assignments = DeliveryAssignment.objects.all()

    if start_date:
        assignments = assignments.filter(assigned_at__gte=start_date)
    if end_date:
        assignments = assignments.filter(assigned_at__lte=end_date)

    # Basic statistics
    total_deliveries = assignments.count()
    completed_deliveries = assignments.filter(status="delivered").count()
    pending_deliveries = assignments.filter(
        status__in=["assigned", "accepted", "picked_up", "in_transit"]
    ).count()
    failed_deliveries = assignments.filter(status="failed").count()

    # Calculate success rate
    success_rate = (
        (completed_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
    )

    # Average delivery time (only for completed deliveries) - Optimized query
    completed_assignments = assignments.filter(
        status="delivered", picked_up_at__isnull=False, delivered_at__isnull=False
    )

    avg_delivery_time = 0
    if completed_assignments.exists():
        # Calculate average using database aggregation for better performance
        time_diffs = []
        for assignment in completed_assignments:
            time_diff = (
                assignment.delivered_at - assignment.picked_up_at
            ).total_seconds() / 3600
            time_diffs.append(time_diff)

        if time_diffs:
            avg_delivery_time = sum(time_diffs) / len(time_diffs)

    # Customer satisfaction (average rating)
    feedback_avg = (
        DeliveryFeedback.objects.aggregate(Avg("overall_rating"))["overall_rating__avg"]
        or 0
    )

    # Zone-wise statistics
    zone_stats = {}
    for zone in DeliveryZone.objects.filter(is_active=True):
        zone_assignments = assignments.filter(delivery_zone=zone)
        zone_total = zone_assignments.count()
        zone_completed = zone_assignments.filter(status="delivered").count()

        zone_stats[zone.name] = {
            "total_deliveries": zone_total,
            "completed_deliveries": zone_completed,
            "average_delivery_fee": float(zone.delivery_fee),
            "success_rate": (
                round((zone_completed / zone_total * 100), 2) if zone_total > 0 else 0
            ),
        }

    # Partner performance
    partner_performance = {}
    for partner in DeliveryPartner.objects.filter(is_active=True):
        partner_assignments = assignments.filter(delivery_partner=partner)
        partner_performance[partner.name] = {
            "total_deliveries": partner_assignments.count(),
            "completed_deliveries": partner_assignments.filter(
                status="delivered"
            ).count(),
            "success_rate": float(partner.success_rate),
            "average_rating": float(partner.rating),
            "average_delivery_time": float(partner.average_delivery_time),
        }

    stats_data = {
        "total_deliveries": total_deliveries,
        "completed_deliveries": completed_deliveries,
        "pending_deliveries": pending_deliveries,
        "failed_deliveries": failed_deliveries,
        "average_delivery_time": round(avg_delivery_time, 2),
        "success_rate": round(success_rate, 2),
        "customer_satisfaction": round(feedback_avg, 2),
        "zone_stats": zone_stats,
        "partner_performance": partner_performance,
    }

    serializer = DeliveryStatsSerializer(stats_data)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def delivery_partners(request):
    """Get all delivery partners"""
    partners = DeliveryPartner.objects.filter(is_active=True)
    serializer = DeliveryPartnerSerializer(partners, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def unassigned_orders(request):
    """Get orders that haven't been assigned for delivery"""
    unassigned_orders = (
        Order.objects.filter(
            payment_status="paid",
            status__in=["confirmed", "processing", "ready_for_pickup"],
        )
        .exclude(delivery_assignment__isnull=False)
        .select_related("customer")
    )

    orders_data = []
    for order in unassigned_orders:
        orders_data.append(
            {
                "id": order.id,
                "order_number": order.order_number,
                "customer_name": order.customer.get_full_name(),
                "delivery_address": order.delivery_address,
                "delivery_city": order.delivery_city,
                "delivery_phone": order.delivery_phone,
                "total_amount": float(order.total_amount),
                "created_at": order.created_at,
                "estimated_delivery_zone": get_suggested_zone(order),
            }
        )

    return Response(orders_data)


def get_suggested_zone(order):
    """Suggest delivery zone based on order address"""
    city = order.delivery_city.lower() if order.delivery_city else ""
    postal_code = (
        order.delivery_postal_code if hasattr(order, "delivery_postal_code") else ""
    )

    # Try to find matching zone
    zone = DeliveryZone.objects.filter(
        Q(cities__icontains=city) | Q(postal_codes__icontains=postal_code),
        is_active=True,
    ).first()

    return DeliveryZoneSerializer(zone).data if zone else None


# Real-time Tracking Updates


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def quick_status_update(request, assignment_id):
    """Quick status update for delivery personnel"""
    if not request.user.is_staff:
        return Response(
            {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
        )

    assignment = get_object_or_404(DeliveryAssignment, id=assignment_id)

    # Predefined quick updates
    quick_updates = {
        "picked_up": {
            "event": "picked_up_from_farm",
            "description": "Order picked up from farm and ready for delivery",
        },
        "out_for_delivery": {
            "event": "out_for_delivery",
            "description": "Out for delivery to customer",
        },
        "delivered": {
            "event": "delivered_successfully",
            "description": "Order delivered successfully to customer",
        },
        "failed": {
            "event": "delivery_failed",
            "description": "Delivery attempt failed",
        },
    }

    update_type = request.data.get("update_type")
    custom_note = request.data.get("note", "")
    location = request.data.get("location", "")

    if update_type not in quick_updates:
        return Response(
            {"error": "Invalid update type", "valid_types": list(quick_updates.keys())},
            status=status.HTTP_400_BAD_REQUEST,
        )

    update_info = quick_updates[update_type]

    # Create tracking event
    tracking = DeliveryTracking.objects.create(
        delivery_assignment=assignment,
        event=update_info["event"],
        description=custom_note or update_info["description"],
        location=location,
        created_by=request.user,
    )

    # Update assignment status
    if update_type == "picked_up":
        assignment.status = "picked_up"
        assignment.picked_up_at = timezone.now()
    elif update_type == "out_for_delivery":
        assignment.status = "in_transit"
    elif update_type == "delivered":
        assignment.status = "delivered"
        assignment.delivered_at = timezone.now()
        assignment.actual_delivery_time = timezone.now()
    elif update_type == "failed":
        assignment.status = "failed"
        assignment.delivery_issues = custom_note

    assignment.save()

    return Response(
        {
            "message": "Status updated successfully",
            "tracking_event": DeliveryTrackingSerializer(tracking).data,
            "new_status": assignment.status,
        }
    )


# Delivery Route Optimization (Future Enhancement)


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def optimize_routes(request):
    """Optimize delivery routes for efficiency"""
    zone_id = request.GET.get("zone_id")
    date = request.GET.get("date", timezone.now().date())

    if not zone_id:
        return Response(
            {"error": "zone_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Get pending deliveries for the zone and date
    pending_deliveries = DeliveryAssignment.objects.filter(
        delivery_zone_id=zone_id,
        status__in=["assigned", "accepted"],
        assigned_at__date=date,
    ).select_related("order")

    if not pending_deliveries.exists():
        return Response(
            {
                "message": "No pending deliveries found for optimization",
                "deliveries": [],
            }
        )

    # Simple route optimization (in production, use proper algorithms)
    deliveries_data = []
    for delivery in pending_deliveries:
        deliveries_data.append(
            {
                "assignment_id": delivery.id,
                "order_number": delivery.order.order_number,
                "customer_address": delivery.order.delivery_address,
                "customer_phone": delivery.order.delivery_phone,
                "estimated_time": delivery.estimated_delivery_time,
                "priority": "high" if delivery.order.total_amount > 1000 else "normal",
            }
        )

    # Sort by estimated time and priority
    optimized_route = sorted(
        deliveries_data, key=lambda x: (x["priority"] == "normal", x["estimated_time"])
    )

    return Response(
        {
            "message": f"Route optimized for {len(optimized_route)} deliveries",
            "zone_name": DeliveryZone.objects.get(id=zone_id).name,
            "date": date,
            "optimized_route": optimized_route,
            "estimated_total_time": len(optimized_route)
            * 30,  # 30 minutes per delivery
        }
    )

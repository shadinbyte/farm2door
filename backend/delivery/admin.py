# delivery/admin.py

from time import gmtime, timezone

from django.contrib import admin
from django.db.models import Avg, Count
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    DeliveryAssignment,
    DeliveryFeedback,
    DeliveryPartner,
    DeliveryRoute,
    DeliverySlot,
    DeliveryTracking,
    DeliveryZone,
)


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "delivery_fee",
        "estimated_delivery_hours",
        "is_active",
        "total_deliveries",
    )
    list_filter = ("is_active", "delivery_fee")
    search_fields = ("name", "cities", "postal_codes")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Basic Information", {"fields": ("name", "description", "is_active")}),
        ("Geographic Coverage", {"fields": ("postal_codes", "cities")}),
        ("Delivery Settings", {"fields": ("delivery_fee", "estimated_delivery_hours")}),
    )

    def total_deliveries(self, obj):
        return obj.deliveryassignment_set.count()

    total_deliveries.short_description = "Total Deliveries"


@admin.register(DeliveryPartner)
class DeliveryPartnerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "contact_person",
        "phone_number",
        "rating",
        "success_rate",
        "is_active",
    )
    list_filter = ("is_active", "rating", "success_rate")
    search_fields = ("name", "contact_person", "phone_number", "email")
    readonly_fields = (
        "rating",
        "success_rate",
        "average_delivery_time",
        "created_at",
        "updated_at",
    )
    filter_horizontal = ("service_zones",)

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "contact_person",
                    "phone_number",
                    "email",
                    "is_active",
                )
            },
        ),
        (
            "Service Details",
            {"fields": ("service_zones", "business_license", "vehicle_types")},
        ),
        (
            "Performance Metrics",
            {
                "fields": ("rating", "success_rate", "average_delivery_time"),
                "classes": ("collapse",),
            },
        ),
    )


class DeliveryTrackingInline(admin.TabularInline):
    model = DeliveryTracking
    extra = 0
    readonly_fields = ("actual_time", "created_by")
    fields = (
        "event",
        "description",
        "location",
        "estimated_time",
        "actual_time",
        "created_by",
    )


@admin.register(DeliveryAssignment)
class DeliveryAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "order_link",
        "delivery_partner",
        "status",
        "assigned_at",
        "delivery_rating",
    )
    list_filter = ("status", "delivery_partner", "delivery_zone", "assigned_at")
    search_fields = (
        "order__order_number",
        "delivery_partner__name",
        "delivery_person_name",
    )
    readonly_fields = (
        "assigned_at",
        "delivery_duration_hours",
        "created_at",
        "updated_at",
    )
    inlines = [DeliveryTrackingInline]

    fieldsets = (
        (
            "Assignment Details",
            {"fields": ("order", "delivery_partner", "delivery_zone", "status")},
        ),
        (
            "Delivery Personnel",
            {"fields": ("delivery_person_name", "delivery_person_phone")},
        ),
        ("Locations", {"fields": ("pickup_location", "current_location")}),
        (
            "Timing",
            {
                "fields": (
                    "assigned_at",
                    "accepted_at",
                    "picked_up_at",
                    "delivered_at",
                    "estimated_delivery_time",
                    "actual_delivery_time",
                    "delivery_duration_hours",
                )
            },
        ),
        (
            "Notes and Feedback",
            {
                "fields": (
                    "pickup_notes",
                    "delivery_notes",
                    "delivery_rating",
                    "delivery_issues",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def order_link(self, obj):
        url = reverse("admin:orders_order_change", args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)

    order_link.short_description = "Order"

    def delivery_duration_hours(self, obj):
        duration = obj.delivery_duration
        return f"{duration:.1f} hours" if duration else "-"

    delivery_duration_hours.short_description = "Delivery Duration"

    actions = ["mark_as_picked_up", "mark_as_delivered"]

    def mark_as_picked_up(self, request, queryset):
        count = 0
        for assignment in queryset:
            if assignment.status in ["assigned", "accepted"]:
                assignment.status = "picked_up"
                assignment.picked_up_at = timezone.now()
                assignment.save()

                # Create tracking event
                DeliveryTracking.objects.create(
                    delivery_assignment=assignment,
                    event="picked_up_from_farm",
                    description="Marked as picked up via admin",
                    created_by=request.user,
                )
                count += 1

        self.message_user(request, f"{count} deliveries marked as picked up.")

    mark_as_picked_up.short_description = "Mark selected as picked up"

    def mark_as_delivered(self, request, queryset):
        from django.utils import timezone

        count = 0
        for assignment in queryset:
            if assignment.status in ["picked_up", "in_transit"]:
                assignment.status = "delivered"
                assignment.delivered_at = timezone.now()
                assignment.actual_delivery_time = timezone.now()
                assignment.save()

                # Create tracking event
                DeliveryTracking.objects.create(
                    delivery_assignment=assignment,
                    event="delivered_successfully",
                    description="Marked as delivered via admin",
                    created_by=request.user,
                )
                count += 1

        self.message_user(request, f"{count} deliveries marked as delivered.")

    mark_as_delivered.short_description = "Mark selected as delivered"


@admin.register(DeliveryTracking)
class DeliveryTrackingAdmin(admin.ModelAdmin):
    list_display = (
        "delivery_assignment_link",
        "event_display",
        "location",
        "actual_time",
        "created_by",
    )
    list_filter = ("event", "actual_time")
    search_fields = (
        "delivery_assignment__order__order_number",
        "location",
        "description",
    )
    readonly_fields = ("actual_time", "created_at")

    fieldsets = (
        (
            "Tracking Information",
            {"fields": ("delivery_assignment", "event", "description", "location")},
        ),
        (
            "Location Data",
            {"fields": ("latitude", "longitude"), "classes": ("collapse",)},
        ),
        ("Timing", {"fields": ("estimated_time", "actual_time")}),
        (
            "Additional Data",
            {"fields": ("metadata", "created_by"), "classes": ("collapse",)},
        ),
    )

    def delivery_assignment_link(self, obj):
        url = reverse(
            "admin:delivery_deliveryassignment_change",
            args=[obj.delivery_assignment.id],
        )
        return format_html(
            '<a href="{}">{}</a>', url, obj.delivery_assignment.order.order_number
        )

    delivery_assignment_link.short_description = "Delivery Assignment"

    def event_display(self, obj):
        return obj.get_event_display()

    event_display.short_description = "Event"


@admin.register(DeliverySlot)
class DeliverySlotAdmin(admin.ModelAdmin):
    list_display = (
        "delivery_zone",
        "slot_type",
        "time_range",
        "availability",
        "additional_fee",
        "is_active",
    )
    list_filter = ("slot_type", "is_active", "delivery_zone")
    search_fields = ("delivery_zone__name",)

    fieldsets = (
        (
            "Slot Information",
            {"fields": ("delivery_zone", "slot_type", "start_time", "end_time")},
        ),
        ("Capacity", {"fields": ("max_deliveries", "current_bookings")}),
        (
            "Pricing and Availability",
            {"fields": ("additional_fee", "available_days", "is_active")},
        ),
    )

    def time_range(self, obj):
        return f"{obj.start_time} - {obj.end_time}"

    time_range.short_description = "Time Range"

    def availability(self, obj):
        percentage = (
            (obj.max_deliveries - obj.current_bookings) / obj.max_deliveries
        ) * 100
        color = "green" if percentage > 50 else "orange" if percentage > 25 else "red"
        return format_html(
            '<span style="color: {};">{}/{} ({:.1f}%)</span>',
            color,
            obj.current_bookings,
            obj.max_deliveries,
            percentage,
        )

    availability.short_description = "Availability"


@admin.register(DeliveryFeedback)
class DeliveryFeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer_name",
        "overall_rating",
        "delivery_partner",
        "created_at",
    )
    list_filter = (
        "overall_rating",
        "delivery_time_rating",
        "would_recommend",
        "created_at",
    )
    search_fields = ("customer__username", "delivery_assignment__order__order_number")
    readonly_fields = ("created_at",)

    fieldsets = (
        ("Feedback Details", {"fields": ("delivery_assignment", "customer")}),
        (
            "Ratings",
            {
                "fields": (
                    "overall_rating",
                    "delivery_time_rating",
                    "delivery_person_rating",
                    "product_condition_rating",
                )
            },
        ),
        ("Comments", {"fields": ("positive_feedback", "improvement_suggestions")}),
        (
            "Additional Information",
            {
                "fields": ("would_recommend", "delivery_issues"),
                "classes": ("collapse",),
            },
        ),
    )

    def order_number(self, obj):
        return obj.delivery_assignment.order.order_number

    order_number.short_description = "Order Number"

    def customer_name(self, obj):
        return obj.customer.get_full_name()

    customer_name.short_description = "Customer"

    def delivery_partner(self, obj):
        return obj.delivery_assignment.delivery_partner.name

    delivery_partner.short_description = "Delivery Partner"


@admin.register(DeliveryRoute)
class DeliveryRouteAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "delivery_partner",
        "delivery_zone",
        "estimated_duration",
        "total_distance",
        "is_active",
    )
    list_filter = ("is_active", "delivery_partner", "delivery_zone")
    search_fields = ("name", "delivery_partner__name", "start_location")

    fieldsets = (
        (
            "Route Information",
            {"fields": ("name", "delivery_partner", "delivery_zone", "start_location")},
        ),
        (
            "Route Details",
            {"fields": ("route_sequence", "estimated_duration", "total_distance")},
        ),
        (
            "Cost Analysis",
            {"fields": ("fuel_cost", "is_active"), "classes": ("collapse",)},
        ),
    )

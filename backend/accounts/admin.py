from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomerProfile, FarmerProfile, User, UserProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "user_type",
        "is_verified",
        "is_active",
        "date_joined",
    )
    list_filter = ("user_type", "is_verified", "is_active", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name", "phone_number")
    ordering = ("-date_joined",)

    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("user_type", "phone_number", "is_verified")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional Info", {"fields": ("user_type", "phone_number", "email")}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "country", "created_at")
    list_filter = ("country", "city", "created_at")
    search_fields = ("user__username", "user__email", "city")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("User", {"fields": ("user",)}),
        ("Personal Information", {"fields": ("avatar", "bio", "date_of_birth")}),
        (
            "Address",
            {"fields": ("street_address", "city", "state", "postal_code", "country")},
        ),
        ("Location", {"fields": ("latitude", "longitude"), "classes": ("collapse",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "farm_name",
        "user",
        "organic_certified",
        "is_verified",
        "total_sales",
        "rating",
        "created_at",
    )
    list_filter = ("organic_certified", "is_verified", "created_at")
    search_fields = ("farm_name", "user__username", "user__email")
    readonly_fields = (
        "total_sales",
        "rating",
        "total_orders",
        "verified_at",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Basic Info",
            {"fields": ("user", "farm_name", "farm_description", "farm_size")},
        ),
        (
            "Certification",
            {
                "fields": (
                    "organic_certified",
                    "certification_number",
                    "certification_document",
                    "is_verified",
                    "verified_at",
                )
            },
        ),
        ("Location", {"fields": ("farm_address", "farm_latitude", "farm_longitude")}),
        (
            "Business Details",
            {
                "fields": (
                    "business_license",
                    "tax_id",
                    "bank_account_number",
                    "bank_name",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Statistics",
            {
                "fields": ("total_sales", "rating", "total_orders"),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    actions = ["verify_farmers", "unverify_farmers"]

    def verify_farmers(self, request, queryset):
        from django.utils import timezone

        count = queryset.update(is_verified=True, verified_at=timezone.now())
        self.message_user(request, f"{count} farmers verified successfully")

    verify_farmers.short_description = "Verify selected farmers"

    def unverify_farmers(self, request, queryset):
        count = queryset.update(is_verified=False, verified_at=None)
        self.message_user(request, f"{count} farmers unverified")

    unverify_farmers.short_description = "Unverify selected farmers"


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "total_orders",
        "total_spent",
        "loyalty_points",
        "preferred_delivery_time",
        "created_at",
    )
    list_filter = (
        "preferred_delivery_time",
        "email_notifications",
        "sms_notifications",
        "created_at",
    )
    search_fields = ("user__username", "user__email")
    readonly_fields = (
        "total_orders",
        "total_spent",
        "loyalty_points",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("User", {"fields": ("user",)}),
        ("Preferences", {"fields": ("preferred_delivery_time",)}),
        ("Statistics", {"fields": ("total_orders", "total_spent", "loyalty_points")}),
        (
            "Notifications",
            {
                "fields": (
                    "email_notifications",
                    "sms_notifications",
                    "push_notifications",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

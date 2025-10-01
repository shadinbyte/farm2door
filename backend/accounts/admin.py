# accounts/admin.py

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


@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "farm_name",
        "user",
        "organic_certified",
        "is_verified",
        "total_sales",
        "rating",
    )
    list_filter = ("organic_certified", "is_verified", "created_at")
    search_fields = ("farm_name", "user__username", "user__email")
    readonly_fields = (
        "total_sales",
        "rating",
        "total_orders",
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
            {"fields": ("organic_certified", "certification_number", "is_verified")},
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
                )
            },
        ),
        (
            "Statistics",
            {
                "fields": ("total_sales", "rating", "total_orders"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "total_orders",
        "total_spent",
        "loyalty_points",
        "preferred_delivery_time",
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

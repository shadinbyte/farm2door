# payments/admin.py

from django.contrib import admin
from django.utils.html import format_html

from .models import FarmerEarnings, PaymentMethod, SSLCommerzTransaction, Transaction


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "name",
        "is_active",
        "processing_fee_percentage",
        "fixed_fee",
    )
    list_filter = ("is_active", "name")
    search_fields = ("display_name", "name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_id",
        "user",
        "order_link",
        "transaction_type",
        "status",
        "amount",
        "initiated_at",
    )
    list_filter = ("status", "transaction_type", "payment_method", "initiated_at")
    search_fields = (
        "transaction_id",
        "reference_id",
        "user__username",
        "order__order_number",
    )
    readonly_fields = ("transaction_id", "net_amount", "initiated_at", "completed_at")

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "transaction_id",
                    "reference_id",
                    "transaction_type",
                    "status",
                )
            },
        ),
        ("Related Objects", {"fields": ("order", "user", "payment_method")}),
        ("Amount Details", {"fields": ("amount", "fee_amount", "net_amount")}),
        (
            "Response Data",
            {
                "fields": ("gateway_response", "failure_reason"),
                "classes": ("collapse",),
            },
        ),
        ("Timestamps", {"fields": ("initiated_at", "completed_at")}),
    )

    def order_link(self, obj):
        if obj.order:
            return format_html(
                '<a href="/admin/orders/order/{}/change/">{}</a>',
                obj.order.id,
                obj.order.order_number,
            )
        return "-"

    order_link.short_description = "Order"


@admin.register(SSLCommerzTransaction)
class SSLCommerzTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "session_key",
        "transaction_link",
        "val_id",
        "status",
        "amount",
        "card_type",
    )
    list_filter = ("status", "card_type", "card_brand", "risk_level", "created_at")
    search_fields = (
        "session_key",
        "val_id",
        "bank_tran_id",
        "transaction__transaction_id",
    )
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("transaction", "session_key", "gateway_page_url")},
        ),
        (
            "SSLCommerz Response",
            {"fields": ("val_id", "amount", "status", "bank_tran_id", "tran_date")},
        ),
        (
            "Card Information",
            {
                "fields": (
                    "card_type",
                    "card_no",
                    "card_issuer",
                    "card_brand",
                    "card_sub_brand",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Risk Assessment",
            {"fields": ("risk_level", "risk_title"), "classes": ("collapse",)},
        ),
        (
            "Additional Details",
            {"fields": ("store_amount", "currency", "error"), "classes": ("collapse",)},
        ),
    )

    def transaction_link(self, obj):
        return format_html(
            '<a href="/admin/payments/transaction/{}/change/">{}</a>',
            obj.transaction.id,
            obj.transaction.transaction_id,
        )

    transaction_link.short_description = "Transaction"


@admin.register(FarmerEarnings)
class FarmerEarningsAdmin(admin.ModelAdmin):
    list_display = (
        "farmer_name",
        "order_link",
        "gross_amount",
        "platform_commission",
        "net_earnings",
        "is_paid_out",
    )
    list_filter = ("is_paid_out", "created_at")
    search_fields = (
        "farmer__farm_name",
        "farmer__user__username",
        "order__order_number",
    )
    readonly_fields = ("created_at",)

    fieldsets = (
        ("Basic Information", {"fields": ("farmer", "order")}),
        (
            "Earnings Breakdown",
            {"fields": ("gross_amount", "platform_commission", "net_earnings")},
        ),
        (
            "Payout Information",
            {"fields": ("is_paid_out", "payout_date", "payout_reference")},
        ),
    )

    def farmer_name(self, obj):
        return obj.farmer.farm_name

    farmer_name.short_description = "Farm"

    def order_link(self, obj):
        return format_html(
            '<a href="/admin/orders/order/{}/change/">{}</a>',
            obj.order.id,
            obj.order.order_number,
        )

    order_link.short_description = "Order"

    actions = ["mark_as_paid"]

    def mark_as_paid(self, request, queryset):
        from django.utils import timezone

        count = queryset.update(is_paid_out=True, payout_date=timezone.now())
        self.message_user(request, f"{count} earnings marked as paid out.")

    mark_as_paid.short_description = "Mark selected earnings as paid out"

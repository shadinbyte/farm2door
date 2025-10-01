# payments/models.py

from accounts.models import User
from django.core.validators import MinValueValidator
from django.db import models
from orders.models import Order


class PaymentMethod(models.Model):
    METHOD_CHOICES = [
        ("sslcommerz_card", "Credit/Debit Card (SSLCommerz)"),
        ("sslcommerz_bkash", "bKash"),
        ("sslcommerz_rocket", "Rocket"),
        ("sslcommerz_nagad", "Nagad"),
        ("sslcommerz_upay", "Upay"),
        ("bank_transfer", "Direct Bank Transfer"),
        ("cash_on_delivery", "Cash on Delivery"),
    ]

    name = models.CharField(max_length=50, choices=METHOD_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, blank=True)  # Icon class or URL
    is_active = models.BooleanField(default=True)
    processing_fee_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )
    fixed_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    minimum_amount = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    maximum_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # SSLCommerz specific
    sslcz_gateway_name = models.CharField(
        max_length=50, blank=True, help_text="SSLCommerz gateway identifier"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name

    def calculate_total_fee(self, amount):
        """Calculate total fee for given amount"""
        percentage_fee = amount * (self.processing_fee_percentage / 100)
        return percentage_fee + self.fixed_fee


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ("payment", "Payment"),
        ("refund", "Refund"),
        ("withdrawal", "Withdrawal"),
        ("commission", "Commission"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    # Transaction identification
    transaction_id = models.CharField(max_length=100, unique=True, editable=False)
    reference_id = models.CharField(
        max_length=100, blank=True
    )  # External gateway reference

    # Transaction details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Related objects
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="transactions",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transactions"
    )
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)

    # Amount details
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    fee_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Gateway response
    gateway_response = models.JSONField(blank=True, null=True)
    failure_reason = models.TextField(blank=True)

    # Timestamps
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-initiated_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["order", "status"]),
            models.Index(fields=["transaction_id"]),
        ]

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.amount}"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            import uuid

            self.transaction_id = f"TXN{uuid.uuid4().hex[:12].upper()}"

        # Calculate net amount
        self.net_amount = self.amount - self.fee_amount

        super().save(*args, **kwargs)


class FarmerEarnings(models.Model):
    farmer = models.ForeignKey(
        "accounts.FarmerProfile", on_delete=models.CASCADE, related_name="earnings"
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    # Earnings breakdown
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_commission = models.DecimalField(max_digits=6, decimal_places=2)
    net_earnings = models.DecimalField(max_digits=10, decimal_places=2)

    # Payout status
    is_paid_out = models.BooleanField(default=False)
    payout_date = models.DateTimeField(null=True, blank=True)
    payout_reference = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["farmer", "order"]


class SSLCommerzTransaction(models.Model):
    """SSLCommerz specific transaction details"""

    transaction = models.OneToOneField(
        Transaction, on_delete=models.CASCADE, related_name="sslcz_details"
    )

    # SSLCommerz required fields
    session_key = models.CharField(max_length=255, unique=True)
    gateway_page_url = models.URLField(blank=True)

    # SSLCommerz response fields
    val_id = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    card_type = models.CharField(max_length=50, blank=True)
    store_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    card_no = models.CharField(max_length=20, blank=True)
    bank_tran_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=50, blank=True)
    tran_date = models.CharField(max_length=50, blank=True)
    error = models.TextField(blank=True)
    currency = models.CharField(max_length=10, default="BDT")
    card_issuer = models.CharField(max_length=100, blank=True)
    card_brand = models.CharField(max_length=50, blank=True)
    card_sub_brand = models.CharField(max_length=50, blank=True)
    card_issuer_country = models.CharField(max_length=100, blank=True)
    card_issuer_country_code = models.CharField(max_length=10, blank=True)

    # Risk and verification
    risk_level = models.CharField(max_length=10, blank=True)
    risk_title = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SSLCommerz - {self.session_key}"

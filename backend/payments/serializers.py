# payments/serializers.py

from decimal import Decimal

from orders.models import Order
from rest_framework import serializers

from .models import FarmerEarnings, PaymentMethod, SSLCommerzTransaction, Transaction


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = [
            "id",
            "name",
            "display_name",
            "icon",
            "is_active",
            "processing_fee_percentage",
            "fixed_fee",
            "minimum_amount",
            "maximum_amount",
        ]


class InitiatePaymentSerializer(serializers.Serializer):
    order_number = serializers.CharField(max_length=20)
    payment_method = serializers.CharField(max_length=50)
    gateway_preference = serializers.CharField(max_length=50, required=False)

    def validate_order_number(self, value):
        try:
            order = Order.objects.get(order_number=value)
            if order.payment_status != "pending":
                raise serializers.ValidationError(
                    "Order has already been paid or payment is processing"
                )
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found")

    def validate_payment_method(self, value):
        try:
            payment_method = PaymentMethod.objects.get(name=value, is_active=True)
            return value
        except PaymentMethod.DoesNotExist:
            raise serializers.ValidationError("Payment method not available")


class TransactionSerializer(serializers.ModelSerializer):
    payment_method_name = serializers.CharField(
        source="payment_method.display_name", read_only=True
    )
    order_number = serializers.CharField(source="order.order_number", read_only=True)
    customer_name = serializers.CharField(source="user.get_full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "transaction_id",
            "reference_id",
            "transaction_type",
            "status",
            "status_display",
            "amount",
            "fee_amount",
            "net_amount",
            "payment_method_name",
            "order_number",
            "customer_name",
            "initiated_at",
            "completed_at",
        ]


class SSLCommerzTransactionSerializer(serializers.ModelSerializer):
    transaction_details = TransactionSerializer(source="transaction", read_only=True)

    class Meta:
        model = SSLCommerzTransaction
        fields = [
            "session_key",
            "gateway_page_url",
            "val_id",
            "amount",
            "card_type",
            "store_amount",
            "bank_tran_id",
            "status",
            "tran_date",
            "currency",
            "card_issuer",
            "card_brand",
            "risk_level",
            "transaction_details",
        ]


class PaymentCallbackSerializer(serializers.Serializer):
    """Serializer for SSLCommerz callback data"""

    val_id = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    card_type = serializers.CharField(required=False)
    store_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    card_no = serializers.CharField(required=False)
    bank_tran_id = serializers.CharField(required=False)
    status = serializers.CharField()
    tran_date = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
    currency = serializers.CharField(default="BDT")
    tran_id = serializers.CharField()
    card_issuer = serializers.CharField(required=False)
    card_brand = serializers.CharField(required=False)
    card_sub_brand = serializers.CharField(required=False)
    card_issuer_country = serializers.CharField(required=False)
    card_issuer_country_code = serializers.CharField(required=False)
    risk_level = serializers.CharField(required=False)
    risk_title = serializers.CharField(required=False)


class FarmerEarningsSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source="farmer.farm_name", read_only=True)
    order_number = serializers.CharField(source="order.order_number", read_only=True)

    class Meta:
        model = FarmerEarnings
        fields = [
            "id",
            "farmer_name",
            "order_number",
            "gross_amount",
            "platform_commission",
            "net_earnings",
            "is_paid_out",
            "payout_date",
            "payout_reference",
            "created_at",
        ]


class PaymentSummarySerializer(serializers.Serializer):
    """Summary of payment information for order"""

    order_number = serializers.CharField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = serializers.DecimalField(max_digits=6, decimal_places=2)
    tax_amount = serializers.DecimalField(max_digits=6, decimal_places=2)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    available_methods = PaymentMethodSerializer(many=True)

    def to_representation(self, instance):
        """Add calculated fees for each payment method"""
        data = super().to_representation(instance)

        # Add fee calculation for each payment method
        for method in data["available_methods"]:
            method_name = method["name"]
            fee = calculate_payment_fee(data["total_amount"], method_name)
            method["calculated_fee"] = fee
            method["total_with_fee"] = Decimal(str(data["total_amount"])) + fee

        return data


def calculate_payment_fee(amount: Decimal, payment_method: str) -> Decimal:
    """Calculate payment processing fee"""
    fee_rates = {
        "sslcommerz_card": Decimal("2.9"),
        "sslcommerz_bkash": Decimal("1.85"),
        "sslcommerz_rocket": Decimal("1.8"),
        "sslcommerz_nagad": Decimal("1.99"),
        "sslcommerz_upay": Decimal("1.5"),
        "bank_transfer": Decimal("0"),
        "cash_on_delivery": Decimal("0"),
    }

    rate = fee_rates.get(payment_method, Decimal("0"))
    return (amount * rate) / Decimal("100")

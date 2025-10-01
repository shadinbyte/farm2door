# payments/views.py

import logging
from decimal import Decimal

from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from orders.models import Order, OrderTracking
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import FarmerEarnings, PaymentMethod, SSLCommerzTransaction, Transaction
from .serializers import (
    FarmerEarningsSerializer,
    InitiatePaymentSerializer,
    PaymentCallbackSerializer,
    PaymentMethodSerializer,
    PaymentSummarySerializer,
    TransactionSerializer,
)
from .utils import SSLCommerzService, calculate_payment_fee, verify_ipn_hash

logger = logging.getLogger(__name__)

# Payment Methods and Information


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def available_payment_methods(request):
    """Get all available payment methods"""
    methods = PaymentMethod.objects.filter(is_active=True)
    serializer = PaymentMethodSerializer(methods, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def payment_summary(request, order_number):
    """Get payment summary for an order"""
    order = get_object_or_404(Order, order_number=order_number, customer=request.user)

    if order.payment_status != "pending":
        return Response(
            {"error": "Order payment is already processed"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    payment_methods = PaymentMethod.objects.filter(is_active=True)

    summary_data = {
        "order_number": order.order_number,
        "subtotal": order.subtotal,
        "delivery_fee": order.delivery_fee,
        "tax_amount": order.tax_amount,
        "total_amount": order.total_amount,
        "available_methods": payment_methods,
    }

    serializer = PaymentSummarySerializer(summary_data)
    return Response(serializer.data)


# Payment Processing


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def initiate_payment(request):
    """Initiate payment process"""
    if request.user.user_type != "customer":
        return Response(
            {"error": "Only customers can make payments"},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = InitiatePaymentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    order_number = serializer.validated_data["order_number"]
    payment_method_name = serializer.validated_data["payment_method"]
    gateway_preference = serializer.validated_data.get("gateway_preference")

    order = get_object_or_404(Order, order_number=order_number, customer=request.user)
    payment_method = get_object_or_404(PaymentMethod, name=payment_method_name)

    # Handle Cash on Delivery
    if payment_method.name == "cash_on_delivery":
        return handle_cod_payment(order)

    # Handle Bank Transfer
    if payment_method.name == "bank_transfer":
        return handle_bank_transfer_payment(order, payment_method)

    # Handle SSLCommerz payments
    if payment_method.name.startswith("sslcommerz_"):
        return handle_sslcommerz_payment(order, payment_method, gateway_preference)

    return Response(
        {"error": "Payment method not supported"}, status=status.HTTP_400_BAD_REQUEST
    )


def handle_cod_payment(order):
    """Handle Cash on Delivery payment"""
    try:
        with transaction.atomic():
            # Create transaction record
            txn = Transaction.objects.create(
                order=order,
                user=order.customer,
                payment_method=PaymentMethod.objects.get(name="cash_on_delivery"),
                transaction_type="payment",
                amount=order.total_amount,
                fee_amount=0,
                status="completed",
            )

            # Update order payment status
            order.payment_status = "paid"
            order.save()

            # Create order tracking
            OrderTracking.objects.create(
                order=order,
                status="farmer_confirmed",
                description="Payment confirmed (Cash on Delivery). Order sent to farmer.",
                updated_by=order.customer,
            )

            # Calculate farmer earnings
            calculate_farmer_earnings(order)

            return Response(
                {
                    "message": "Cash on Delivery order confirmed",
                    "transaction_id": txn.transaction_id,
                    "payment_method": "Cash on Delivery",
                },
                status=status.HTTP_201_CREATED,
            )

    except Exception as e:
        logger.error(f"COD payment error for order {order.order_number}: {str(e)}")
        return Response(
            {"error": "Payment processing failed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def handle_bank_transfer_payment(order, payment_method):
    """Handle Direct Bank Transfer payment"""
    try:
        with transaction.atomic():
            # Create pending transaction
            txn = Transaction.objects.create(
                order=order,
                user=order.customer,
                payment_method=payment_method,
                transaction_type="payment",
                amount=order.total_amount,
                fee_amount=0,
                status="pending",
            )

            # Update order payment status to processing
            order.payment_status = "pending"
            order.save()

            return Response(
                {
                    "message": "Bank transfer payment initiated",
                    "transaction_id": txn.transaction_id,
                    "payment_method": "Bank Transfer",
                    "bank_details": {
                        "account_name": "Farm2Door Ltd.",
                        "account_number": "1234567890123",
                        "bank_name": "Dutch Bangla Bank",
                        "routing_number": "090",
                        "reference": f"F2D-{order.order_number}",
                    },
                    "instructions": "Please transfer the exact amount and use the reference number. Upload transfer receipt for verification.",
                },
                status=status.HTTP_201_CREATED,
            )

    except Exception as e:
        logger.error(
            f"Bank transfer payment error for order {order.order_number}: {str(e)}"
        )
        return Response(
            {"error": "Payment processing failed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def handle_sslcommerz_payment(order, payment_method, gateway_preference=None):
    """Handle SSLCommerz payment processing"""
    try:
        with transaction.atomic():
            # Calculate payment fee
            fee_amount = calculate_payment_fee(order.total_amount, payment_method.name)
            total_with_fee = order.total_amount + fee_amount

            # Create pending transaction
            txn = Transaction.objects.create(
                order=order,
                user=order.customer,
                payment_method=payment_method,
                transaction_type="payment",
                amount=total_with_fee,
                fee_amount=fee_amount,
                status="pending",
            )

            # Prepare order data for SSLCommerz
            sslcz_service = SSLCommerzService()
            order_data = {
                "order_number": order.order_number,
                "order_id": order.id,
                "amount": total_with_fee,
                "customer_id": order.customer.id,
                "customer_name": f"{order.customer.first_name} {order.customer.last_name}",
                "customer_email": order.customer.email,
                "customer_phone": order.delivery_phone,
                "customer_address": order.delivery_address,
                "customer_city": order.delivery_city,
                "customer_postcode": order.delivery_postal_code,
                "delivery_address": order.delivery_address,
                "delivery_city": order.delivery_city,
                "delivery_postcode": order.delivery_postal_code,
                "items_count": order.items.count(),
                "preferred_gateway": gateway_preference,
            }

            # Create payment session
            session_result = sslcz_service.create_payment_session(order_data)

            if session_result["status"] == "success":
                # Create SSLCommerz transaction record
                sslcz_txn = SSLCommerzTransaction.objects.create(
                    transaction=txn,
                    session_key=session_result["session_key"],
                    gateway_page_url=session_result["gateway_page_url"],
                    amount=total_with_fee,
                    currency="BDT",
                )

                # Update order payment status
                order.payment_status = "pending"
                order.save()

                return Response(
                    {
                        "message": "Payment session created successfully",
                        "transaction_id": txn.transaction_id,
                        "session_key": session_result["session_key"],
                        "payment_url": session_result["gateway_page_url"],
                        "redirect_url": session_result.get("redirect_url"),
                        "total_amount": total_with_fee,
                        "fee_amount": fee_amount,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                # Delete the failed transaction
                txn.status = "failed"
                txn.failure_reason = session_result["error_message"]
                txn.save()

                return Response(
                    {"error": session_result["error_message"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    except Exception as e:
        logger.error(
            f"SSLCommerz payment error for order {order.order_number}: {str(e)}"
        )
        return Response(
            {"error": "Payment processing failed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# SSLCommerz Callback Handlers


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def sslcommerz_success(request):
    """Handle successful payment callback from SSLCommerz"""
    serializer = PaymentCallbackSerializer(data=request.data)
    if not serializer.is_valid():
        logger.error(f"Invalid SSLCommerz success callback data: {serializer.errors}")
        return redirect("/payment/failed/")

    callback_data = serializer.validated_data
    session_key = callback_data["tran_id"]
    val_id = callback_data["val_id"]
    amount = callback_data["amount"]

    try:
        # Find the transaction
        sslcz_txn = get_object_or_404(SSLCommerzTransaction, session_key=session_key)
        txn = sslcz_txn.transaction
        order = txn.order

        # Validate payment with SSLCommerz
        sslcz_service = SSLCommerzService()
        validation_result = sslcz_service.validate_payment(val_id, amount, session_key)

        if validation_result["status"] == "valid":
            with transaction.atomic():
                # Update SSLCommerz transaction details
                update_sslcz_transaction(sslcz_txn, callback_data)

                # Update main transaction
                txn.status = "completed"
                txn.reference_id = val_id
                txn.completed_at = timezone.now()
                txn.gateway_response = validation_result["validation_data"]
                txn.save()

                # Update order
                order.payment_status = "paid"
                order.save()

                # Create order tracking
                OrderTracking.objects.create(
                    order=order,
                    status="farmer_confirmed",
                    description=f'Payment confirmed via {callback_data.get("card_type", "SSLCommerz")}',
                    updated_by=order.customer,
                )

                # Calculate farmer earnings
                calculate_farmer_earnings(order)

                # Send confirmation email (implement later)
                # send_payment_confirmation_email.delay(order.id)

                logger.info(
                    f"Payment successful for order {order.order_number}, transaction {txn.transaction_id}"
                )
                return redirect(f"/payment/success/?order={order.order_number}")
        else:
            # Payment validation failed
            txn.status = "failed"
            txn.failure_reason = validation_result["error_message"]
            txn.save()

            logger.warning(
                f"Payment validation failed for order {order.order_number}: {validation_result['error_message']}"
            )
            return redirect(f"/payment/failed/?order={order.order_number}")

    except Exception as e:
        logger.error(f"Error processing payment success callback: {str(e)}")
        return redirect("/payment/failed/")


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def sslcommerz_fail(request):
    """Handle failed payment callback from SSLCommerz"""
    callback_data = request.data
    session_key = callback_data.get("tran_id")

    try:
        if session_key:
            sslcz_txn = get_object_or_404(
                SSLCommerzTransaction, session_key=session_key
            )
            txn = sslcz_txn.transaction

            # Update transaction status
            txn.status = "failed"
            txn.failure_reason = callback_data.get("error", "Payment failed")
            txn.save()

            # Update SSLCommerz transaction
            update_sslcz_transaction(sslcz_txn, callback_data)

            logger.warning(f"Payment failed for transaction {txn.transaction_id}")
            return redirect(f"/payment/failed/?order={txn.order.order_number}")
        else:
            return redirect("/payment/failed/")

    except Exception as e:
        logger.error(f"Error processing payment failure callback: {str(e)}")
        return redirect("/payment/failed/")


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def sslcommerz_cancel(request):
    """Handle cancelled payment callback from SSLCommerz"""
    callback_data = request.data
    session_key = callback_data.get("tran_id")

    try:
        if session_key:
            sslcz_txn = get_object_or_404(
                SSLCommerzTransaction, session_key=session_key
            )
            txn = sslcz_txn.transaction

            # Update transaction status
            txn.status = "cancelled"
            txn.failure_reason = "Payment cancelled by user"
            txn.save()

            logger.info(
                f"Payment cancelled by user for transaction {txn.transaction_id}"
            )
            return redirect(f"/payment/cancelled/?order={txn.order.order_number}")
        else:
            return redirect("/payment/cancelled/")

    except Exception as e:
        logger.error(f"Error processing payment cancellation: {str(e)}")
        return redirect("/payment/cancelled/")


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def sslcommerz_ipn(request):
    """Handle Instant Payment Notification from SSLCommerz"""
    ipn_data = request.data

    # Verify IPN hash
    if not verify_ipn_hash(ipn_data):
        logger.warning("Invalid IPN hash received from SSLCommerz")
        return HttpResponse("Invalid hash", status=400)

    session_key = ipn_data.get("tran_id")
    val_id = ipn_data.get("val_id")
    status = ipn_data.get("status")

    try:
        sslcz_txn = get_object_or_404(SSLCommerzTransaction, session_key=session_key)
        txn = sslcz_txn.transaction

        # Update transaction based on IPN status
        if status == "VALID":
            if txn.status == "pending":
                txn.status = "completed"
                txn.reference_id = val_id
                txn.completed_at = timezone.now()
                txn.save()

                # Update order
                txn.order.payment_status = "paid"
                txn.order.save()

                logger.info(
                    f"IPN confirmed payment for transaction {txn.transaction_id}"
                )
        elif status in ["FAILED", "CANCELLED"]:
            txn.status = status.lower()
            txn.failure_reason = ipn_data.get("error", f"Payment {status.lower()}")
            txn.save()

        # Update SSLCommerz transaction details
        update_sslcz_transaction(sslcz_txn, ipn_data)

        return HttpResponse("OK", status=200)

    except Exception as e:
        logger.error(f"Error processing IPN: {str(e)}")
        return HttpResponse("Error", status=500)


# Helper Functions


def update_sslcz_transaction(sslcz_txn, callback_data):
    """Update SSLCommerz transaction with callback data"""
    sslcz_txn.val_id = callback_data.get("val_id", "")
    sslcz_txn.card_type = callback_data.get("card_type", "")
    sslcz_txn.store_amount = callback_data.get("store_amount") or 0
    sslcz_txn.card_no = callback_data.get("card_no", "")
    sslcz_txn.bank_tran_id = callback_data.get("bank_tran_id", "")
    sslcz_txn.status = callback_data.get("status", "")
    sslcz_txn.tran_date = callback_data.get("tran_date", "")
    sslcz_txn.error = callback_data.get("error", "")
    sslcz_txn.card_issuer = callback_data.get("card_issuer", "")
    sslcz_txn.card_brand = callback_data.get("card_brand", "")
    sslcz_txn.card_sub_brand = callback_data.get("card_sub_brand", "")
    sslcz_txn.card_issuer_country = callback_data.get("card_issuer_country", "")
    sslcz_txn.card_issuer_country_code = callback_data.get(
        "card_issuer_country_code", ""
    )
    sslcz_txn.risk_level = callback_data.get("risk_level", "")
    sslcz_txn.risk_title = callback_data.get("risk_title", "")
    sslcz_txn.save()


def calculate_farmer_earnings(order):
    """Calculate and create farmer earnings records"""
    platform_commission_rate = Decimal("5.0")  # 5% commission

    # Group order items by farmer
    farmer_totals = {}
    for item in order.items.all():
        farmer_id = item.farmer.id
        if farmer_id not in farmer_totals:
            farmer_totals[farmer_id] = {
                "farmer": item.farmer,
                "gross_amount": Decimal("0"),
            }
        farmer_totals[farmer_id]["gross_amount"] += item.subtotal

    # Create earnings records
    for farmer_data in farmer_totals.values():
        gross_amount = farmer_data["gross_amount"]
        commission = gross_amount * (platform_commission_rate / 100)
        net_earnings = gross_amount - commission

        FarmerEarnings.objects.create(
            farmer=farmer_data["farmer"],
            order=order,
            gross_amount=gross_amount,
            platform_commission=commission,
            net_earnings=net_earnings,
        )


# Transaction Management Views


class CustomerTransactionListView(generics.ListAPIView):
    """List customer's transactions"""

    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type != "customer":
            return Transaction.objects.none()

        return Transaction.objects.filter(user=self.request.user).order_by(
            "-initiated_at"
        )


class FarmerEarningsListView(generics.ListAPIView):
    """List farmer's earnings"""

    serializer_class = FarmerEarningsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type != "farmer":
            return FarmerEarnings.objects.none()

        return FarmerEarnings.objects.filter(
            farmer=self.request.user.farmer_profile
        ).order_by("-created_at")


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def payment_status(request, transaction_id):
    """Get payment status by transaction ID"""
    try:
        txn = Transaction.objects.get(transaction_id=transaction_id, user=request.user)
        serializer = TransactionSerializer(txn)
        return Response(serializer.data)
    except Transaction.DoesNotExist:
        return Response(
            {"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND
        )

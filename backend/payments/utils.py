# payments/utils.py

import hashlib
from decimal import Decimal
from typing import Any, Dict, Optional

import requests
from decouple import config
from django.conf import settings


class SSLCommerzService:
    def __init__(self):
        self.store_id = config("SSLCZ_STORE_ID")
        self.store_password = config("SSLCZ_STORE_PASSWORD")
        self.is_sandbox = config("SSLCZ_IS_SANDBOX", default=True, cast=bool)

        if self.is_sandbox:
            self.base_url = "https://sandbox.sslcommerz.com"
        else:
            self.base_url = "https://securepay.sslcommerz.com"

    def generate_session_key(self, order_number: str) -> str:
        """Generate unique session key for transaction"""
        import time
        import uuid

        return f"{order_number}_{int(time.time())}_{uuid.uuid4().hex[:8]}"

    def create_payment_session(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create payment session with SSLCommerz"""

        session_key = self.generate_session_key(order_data["order_number"])

        # Required parameters for SSLCommerz
        post_data = {
            "store_id": self.store_id,
            "store_passwd": self.store_password,
            "total_amount": str(order_data["amount"]),
            "currency": "BDT",
            "tran_id": session_key,
            "success_url": config("SSLCZ_SUCCESS_URL"),
            "fail_url": config("SSLCZ_FAIL_URL"),
            "cancel_url": config("SSLCZ_CANCEL_URL"),
            "ipn_url": config("SSLCZ_IPN_URL"),
            # Customer information
            "cus_name": order_data["customer_name"],
            "cus_email": order_data["customer_email"],
            "cus_add1": order_data["customer_address"],
            "cus_city": order_data["customer_city"],
            "cus_postcode": order_data["customer_postcode"],
            "cus_country": "Bangladesh",
            "cus_phone": order_data["customer_phone"],
            # Product information
            "product_name": f"Farm2Door Order #{order_data['order_number']}",
            "product_category": "Farm Products",
            "product_profile": "general",
            # Shipping information (same as customer for now)
            "ship_name": order_data["customer_name"],
            "ship_add1": order_data["delivery_address"],
            "ship_city": order_data["delivery_city"],
            "ship_postcode": order_data["delivery_postcode"],
            "ship_country": "Bangladesh",
            # Additional parameters
            "shipping_method": "NO",
            "num_of_item": order_data.get("items_count", 1),
            "value_a": order_data["order_id"],  # Store order ID for reference
            "value_b": order_data["customer_id"],  # Store customer ID
        }

        # Optional: Add specific gateway if provided
        if order_data.get("preferred_gateway"):
            post_data["multi_card_name"] = order_data["preferred_gateway"]

        try:
            response = requests.post(
                f"{self.base_url}/gwprocess/v4/api.php", data=post_data, timeout=30
            )
            response.raise_for_status()
            result = response.json()

            if result.get("status") == "SUCCESS":
                return {
                    "status": "success",
                    "session_key": session_key,
                    "gateway_page_url": result.get("GatewayPageURL"),
                    "redirect_url": result.get("redirectGatewayURL"),
                    "response_data": result,
                }
            else:
                return {
                    "status": "error",
                    "error_message": result.get(
                        "failedreason", "Payment session creation failed"
                    ),
                    "response_data": result,
                }

        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error_message": f"Network error: {str(e)}",
                "response_data": None,
            }
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Unexpected error: {str(e)}",
                "response_data": None,
            }

    def validate_payment(
        self, val_id: str, amount: Decimal, session_key: str
    ) -> Dict[str, Any]:
        """Validate payment with SSLCommerz"""

        validation_data = {
            "val_id": val_id,
            "store_id": self.store_id,
            "store_passwd": self.store_password,
            "format": "json",
        }

        try:
            if self.is_sandbox:
                validation_url = "https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php"
            else:
                validation_url = "https://securepay.sslcommerz.com/validator/api/validationserverAPI.php"

            response = requests.post(validation_url, data=validation_data, timeout=30)
            response.raise_for_status()
            result = response.json()

            # Validate amount and session key
            if (
                result.get("status") == "VALID"
                and result.get("tran_id") == session_key
                and Decimal(result.get("amount", 0)) == amount
            ):

                return {"status": "valid", "validation_data": result}
            else:
                return {
                    "status": "invalid",
                    "error_message": "Payment validation failed",
                    "validation_data": result,
                }

        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error_message": f"Validation request failed: {str(e)}",
                "validation_data": None,
            }
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Validation error: {str(e)}",
                "validation_data": None,
            }

    def get_available_gateways(self) -> list:
        """Get list of available payment gateways"""
        return [
            {
                "gateway": "bkash",
                "name": "bKash",
                "type": "mobile_banking",
                "icon": "bkash-icon",
                "fee_percentage": 1.85,
            },
            {
                "gateway": "rocket",
                "name": "Rocket",
                "type": "mobile_banking",
                "icon": "rocket-icon",
                "fee_percentage": 1.8,
            },
            {
                "gateway": "nagad",
                "name": "Nagad",
                "type": "mobile_banking",
                "icon": "nagad-icon",
                "fee_percentage": 1.99,
            },
            {
                "gateway": "upay",
                "name": "Upay",
                "type": "mobile_banking",
                "icon": "upay-icon",
                "fee_percentage": 1.5,
            },
            {
                "gateway": "visa",
                "name": "Visa Card",
                "type": "credit_card",
                "icon": "visa-icon",
                "fee_percentage": 2.9,
            },
            {
                "gateway": "master",
                "name": "MasterCard",
                "type": "credit_card",
                "icon": "mastercard-icon",
                "fee_percentage": 2.9,
            },
            {
                "gateway": "amex",
                "name": "American Express",
                "type": "credit_card",
                "icon": "amex-icon",
                "fee_percentage": 3.5,
            },
        ]


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


def generate_order_hash(order_data: Dict[str, Any]) -> str:
    """Generate hash for order verification"""
    hash_string = (
        f"{order_data['order_number']}{order_data['amount']}{order_data['customer_id']}"
    )
    return hashlib.sha256(hash_string.encode()).hexdigest()


def verify_ipn_hash(ipn_data: Dict[str, Any]) -> bool:
    """Verify IPN hash from SSLCommerz"""
    received_hash = ipn_data.get("verify_sign", "")
    verify_key = ipn_data.get("verify_key", "")

    # Create verification string
    verify_string = f"{config('SSLCZ_STORE_PASSWORD')}{verify_key}"
    calculated_hash = hashlib.md5(verify_string.encode()).hexdigest()

    return received_hash.upper() == calculated_hash.upper()

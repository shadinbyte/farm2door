# payments/urls.py

from django.urls import path

from . import views

urlpatterns = [
    # Payment methods and information
    path("methods/", views.available_payment_methods, name="payment_methods"),
    path("summary/<str:order_number>/", views.payment_summary, name="payment_summary"),
    # Payment processing
    path("initiate/", views.initiate_payment, name="initiate_payment"),
    path("status/<str:transaction_id>/", views.payment_status, name="payment_status"),
    # SSLCommerz callbacks
    path("sslcommerz/success/", views.sslcommerz_success, name="sslcommerz_success"),
    path("sslcommerz/fail/", views.sslcommerz_fail, name="sslcommerz_fail"),
    path("sslcommerz/cancel/", views.sslcommerz_cancel, name="sslcommerz_cancel"),
    path("sslcommerz/ipn/", views.sslcommerz_ipn, name="sslcommerz_ipn"),
    # Transaction management
    path(
        "my-transactions/",
        views.CustomerTransactionListView.as_view(),
        name="customer_transactions",
    ),
    path(
        "farmer/earnings/",
        views.FarmerEarningsListView.as_view(),
        name="farmer_earnings",
    ),
]

# orders/urls.py

from django.urls import path

from . import views

urlpatterns = [
    # Cart management
    path("cart/", views.get_cart, name="get_cart"),
    path("cart/add/", views.add_to_cart, name="add_to_cart"),
    path(
        "cart/items/<int:item_id>/update/",
        views.update_cart_item,
        name="update_cart_item",
    ),
    path(
        "cart/items/<int:item_id>/remove/",
        views.remove_from_cart,
        name="remove_from_cart",
    ),
    path("cart/clear/", views.clear_cart, name="clear_cart"),
    # Order creation
    path("create/", views.CreateOrderView.as_view(), name="create_order"),
    # Customer order management
    path("my-orders/", views.CustomerOrderListView.as_view(), name="customer_orders"),
    path(
        "my-orders/<str:order_number>/",
        views.CustomerOrderDetailView.as_view(),
        name="customer_order_detail",
    ),
    path("<str:order_number>/cancel/", views.cancel_order, name="cancel_order"),
    # Farmer order management
    path("farmer/orders/", views.FarmerOrderListView.as_view(), name="farmer_orders"),
    path(
        "farmer/orders/<str:order_number>/",
        views.FarmerOrderDetailView.as_view(),
        name="farmer_order_detail",
    ),
    # Order tracking
    path(
        "<str:order_number>/status/update/",
        views.update_order_status,
        name="update_order_status",
    ),
    # Admin views
    path("admin/all/", views.admin_orders, name="admin_orders"),
    # Utility
    path("statuses/", views.order_statuses, name="order_statuses"),
]

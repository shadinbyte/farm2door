# delivery/urls.py

from django.urls import path

from . import views

urlpatterns = [
    # Public delivery information
    path("zones/", views.delivery_zones, name="delivery_zones"),
    path("slots/", views.delivery_slots, name="delivery_slots"),
    path("estimate/", views.estimate_delivery_time, name="estimate_delivery_time"),
    # Customer tracking
    path("track/<str:order_number>/", views.track_delivery, name="track_delivery"),
    path(
        "customer/history/",
        views.CustomerDeliveryHistoryView.as_view(),
        name="customer_delivery_history",
    ),
    # Delivery feedback
    path(
        "feedback/create/",
        views.DeliveryFeedbackCreateView.as_view(),
        name="create_delivery_feedback",
    ),
    path(
        "feedback/list/",
        views.DeliveryFeedbackListView.as_view(),
        name="delivery_feedback_list",
    ),
    # Partner/Staff views
    path(
        "partner/assignments/",
        views.PartnerDeliveryListView.as_view(),
        name="partner_delivery_list",
    ),
    path(
        "assignment/<int:assignment_id>/update-status/",
        views.update_delivery_status,
        name="update_delivery_status",
    ),
    path(
        "assignment/<int:assignment_id>/quick-update/",
        views.quick_status_update,
        name="quick_status_update",
    ),
    # Admin management
    path("admin/assign/<int:order_id>/", views.assign_delivery, name="assign_delivery"),
    path("admin/statistics/", views.delivery_statistics, name="delivery_statistics"),
    path("admin/partners/", views.delivery_partners, name="delivery_partners"),
    path("admin/unassigned-orders/", views.unassigned_orders, name="unassigned_orders"),
    path("admin/optimize-routes/", views.optimize_routes, name="optimize_routes"),
]

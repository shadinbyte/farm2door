from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    # Authentication
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Profile management
    path("profile/", views.profile, name="profile"),
    path(
        "profile/update/", views.UpdateUserProfileView.as_view(), name="update_profile"
    ),
    path(
        "farmer/profile/update/",
        views.UpdateFarmerProfileView.as_view(),
        name="update_farmer_profile",
    ),
    path(
        "customer/profile/update/",
        views.UpdateCustomerProfileView.as_view(),
        name="update_customer_profile",
    ),
    # Password management
    path("change-password/", views.change_password, name="change_password"),
    # Farmers
    path("farmers/", views.verified_farmers_list, name="verified_farmers_list"),
    path("farmers/<int:farmer_id>/", views.farmer_detail, name="farmer_detail"),
    # Admin
    path("users/", views.all_users, name="all_users"),
]

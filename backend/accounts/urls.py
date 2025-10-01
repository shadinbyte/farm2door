# accounts/urls.py

from django.urls import path

from . import views

urlpatterns = [
    # Authentication
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # Profile management
    path("profile/", views.profile, name="profile"),
    path("profile/update/", views.UpdateProfileView.as_view(), name="update_profile"),
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
    # Admin and public views
    path("users/", views.all_users, name="all_users"),
    path("farmers/", views.farmers_list, name="farmers_list"),
]

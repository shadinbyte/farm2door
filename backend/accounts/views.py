# accounts/views.py

from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import CustomerProfile, FarmerProfile, User, UserProfile
from .serializers import (
    CustomerProfileSerializer,
    FarmerProfileSerializer,
    LoginSerializer,
    PasswordChangeSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register(request):
    """Register a new user (farmer, customer, or admin)"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "message": "User registered successfully",
                "user": UserSerializer(user).data,
                "token": token.key,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """Login user and return authentication token"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        login(request, user)

        return Response(
            {
                "message": "Login successful",
                "user": UserSerializer(user).data,
                "token": token.key,
            },
            status=status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Logout user and delete token"""
    try:
        request.user.auth_token.delete()
        logout(request)
        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )
    except:
        return Response(
            {"error": "Error logging out"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def profile(request):
    """Get current user profile"""
    user = request.user
    user_data = UserSerializer(user).data

    # Add profile data based on user type
    if user.user_type == "farmer" and hasattr(user, "farmer_profile"):
        profile_data = FarmerProfileSerializer(user.farmer_profile).data
        user_data["farmer_profile"] = profile_data
    elif user.user_type == "customer" and hasattr(user, "customer_profile"):
        profile_data = CustomerProfileSerializer(user.customer_profile).data
        user_data["customer_profile"] = profile_data

    # Add basic user profile if exists
    if hasattr(user, "profile"):
        user_profile_data = UserProfileSerializer(user.profile).data
        user_data["profile"] = user_profile_data

    return Response(user_data, status=status.HTTP_200_OK)


class UpdateProfileView(generics.UpdateAPIView):
    """Update user profile"""

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

    def get_serializer_class(self):
        return UserProfileSerializer


class UpdateFarmerProfileView(generics.UpdateAPIView):
    """Update farmer profile"""

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        if self.request.user.user_type != "farmer":
            return None
        return get_object_or_404(FarmerProfile, user=self.request.user)

    def get_serializer_class(self):
        return FarmerProfileSerializer


class UpdateCustomerProfileView(generics.UpdateAPIView):
    """Update customer profile"""

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        if self.request.user.user_type != "customer":
            return None
        return get_object_or_404(CustomerProfile, user=self.request.user)

    def get_serializer_class(self):
        return CustomerProfileSerializer


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """Change user password"""
    serializer = PasswordChangeSerializer(
        data=request.data, context={"request": request}
    )
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        # Delete old token and create new one
        try:
            user.auth_token.delete()
        except:
            pass
        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {"message": "Password changed successfully", "token": token.key},
            status=status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def all_users(request):
    """Get all users (admin only)"""
    user_type = request.GET.get("user_type")

    users = User.objects.all()
    if user_type:
        users = users.filter(user_type=user_type)

    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def farmers_list(request):
    """Get list of verified farmers (public)"""
    farmers = FarmerProfile.objects.filter(is_verified=True).select_related("user")
    serializer = FarmerProfileSerializer(farmers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

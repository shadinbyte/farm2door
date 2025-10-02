from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomerProfile, FarmerProfile, User, UserProfile
from .serializers import (
    CustomerProfileSerializer,
    FarmerProfileSerializer,
    FarmerProfileUpdateSerializer,
    LoginSerializer,
    PasswordChangeSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register(request):
    """Register a new user"""
    serializer = UserRegistrationSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "User registered successfully",
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """Login user and return JWT tokens"""
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data["user"]

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Login successful",
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Logout user by blacklisting refresh token"""
    try:
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def profile(request):
    """Get current user profile with role-specific data"""
    user = request.user
    user_data = UserSerializer(user).data

    # Add profile data based on user type
    if hasattr(user, "profile"):
        user_data["profile"] = UserProfileSerializer(user.profile).data

    if user.user_type == "farmer" and hasattr(user, "farmer_profile"):
        user_data["farmer_profile"] = FarmerProfileSerializer(user.farmer_profile).data
    elif user.user_type == "customer" and hasattr(user, "customer_profile"):
        user_data["customer_profile"] = CustomerProfileSerializer(
            user.customer_profile
        ).data

    return Response(user_data, status=status.HTTP_200_OK)


class UpdateUserProfileView(generics.UpdateAPIView):
    """Update basic user profile"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user.profile


class UpdateFarmerProfileView(generics.UpdateAPIView):
    """Update farmer profile"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FarmerProfileUpdateSerializer

    def get_object(self):
        if self.request.user.user_type != "farmer":
            return None
        return get_object_or_404(FarmerProfile, user=self.request.user)


class UpdateCustomerProfileView(generics.UpdateAPIView):
    """Update customer profile"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomerProfileSerializer

    def get_object(self):
        if self.request.user.user_type != "customer":
            return None
        return get_object_or_404(CustomerProfile, user=self.request.user)


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

        return Response(
            {"message": "Password changed successfully"},
            status=status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def all_users(request):
    """Get all users (admin only)"""
    user_type = request.query_params.get("user_type")

    users = User.objects.all()
    if user_type:
        users = users.filter(user_type=user_type)

    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def verified_farmers_list(request):
    """Get list of verified farmers (public)"""
    farmers = (
        FarmerProfile.objects.filter(is_verified=True)
        .select_related("user")
        .order_by("-rating")
    )

    serializer = FarmerProfileSerializer(farmers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def farmer_detail(request, farmer_id):
    """Get farmer profile details"""
    farmer = get_object_or_404(
        FarmerProfile.objects.select_related("user"), id=farmer_id
    )

    serializer = FarmerProfileSerializer(farmer)
    return Response(serializer.data, status=status.HTTP_200_OK)

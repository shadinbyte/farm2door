from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomerProfile, FarmerProfile, User, UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "user_type",
            "password",
            "password_confirm",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        return user


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer"""

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "user_type",
            "is_verified",
            "date_joined",
        )
        read_only_fields = ("id", "date_joined", "is_verified")


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""

    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")


class FarmerProfileSerializer(serializers.ModelSerializer):
    """Farmer profile serializer"""

    user = UserSerializer(read_only=True)

    class Meta:
        model = FarmerProfile
        fields = "__all__"
        read_only_fields = (
            "user",
            "total_sales",
            "rating",
            "total_orders",
            "is_verified",
            "verified_at",
            "created_at",
            "updated_at",
        )


class CustomerProfileSerializer(serializers.ModelSerializer):
    """Customer profile serializer"""

    user = UserSerializer(read_only=True)

    class Meta:
        model = CustomerProfile
        fields = "__all__"
        read_only_fields = (
            "user",
            "total_orders",
            "total_spent",
            "loyalty_points",
            "created_at",
            "updated_at",
        )


class LoginSerializer(serializers.Serializer):
    """Login serializer with JWT token generation"""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            user = authenticate(username=username, password=password)

            if not user:
                raise serializers.ValidationError("Invalid credentials")

            if not user.is_active:
                raise serializers.ValidationError("Account is disabled")

            attrs["user"] = user
            return attrs
        else:
            raise serializers.ValidationError("Must include username and password")


class TokenSerializer(serializers.Serializer):
    """Serializer for JWT tokens"""

    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()


class PasswordChangeSerializer(serializers.Serializer):
    """Password change serializer"""

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True, write_only=True, validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password": "Passwords don't match"})
        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value


class FarmerProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating farmer profile"""

    class Meta:
        model = FarmerProfile
        fields = (
            "farm_name",
            "farm_description",
            "farm_size",
            "organic_certified",
            "certification_number",
            "certification_document",
            "farm_address",
            "farm_latitude",
            "farm_longitude",
            "business_license",
            "tax_id",
            "bank_account_number",
            "bank_name",
        )

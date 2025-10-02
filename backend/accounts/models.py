from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Custom User model with user type support"""

    USER_TYPE_CHOICES = (
        ("farmer", "Farmer"),
        ("customer", "Customer"),
        ("admin", "Admin"),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number must be entered in format: '+999999999'. Up to 15 digits.",
    )
    phone_number = models.CharField(
        validators=[phone_regex], max_length=17, unique=True
    )
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user_type", "is_active"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class UserProfile(models.Model):
    """Basic profile for all users"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="profiles/avatars/", blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)

    # Address fields
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default="Bangladesh")

    # Location coordinates
    latitude = models.DecimalField(
        max_digits=22, decimal_places=16, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=22, decimal_places=16, blank=True, null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class FarmerProfile(models.Model):
    """Extended profile for farmers"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="farmer_profile",
        limit_choices_to={"user_type": "farmer"},
    )
    farm_name = models.CharField(max_length=200)
    farm_description = models.TextField(max_length=1000, blank=True)
    farm_size = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Farm size in acres",
        blank=True,
        null=True,
    )

    # Certification
    organic_certified = models.BooleanField(default=False)
    certification_number = models.CharField(max_length=100, blank=True)
    certification_document = models.FileField(
        upload_to="farmers/certifications/", blank=True, null=True
    )

    # Farm location
    farm_address = models.TextField(max_length=500, blank=True)
    farm_latitude = models.DecimalField(
        max_digits=22, decimal_places=16, blank=True, null=True
    )
    farm_longitude = models.DecimalField(
        max_digits=22, decimal_places=16, blank=True, null=True
    )

    # Business details
    business_license = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)

    # Platform statistics
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_orders = models.IntegerField(default=0)

    # Verification
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.farm_name} - {self.user.username}"


class CustomerProfile(models.Model):
    """Extended profile for customers"""

    DELIVERY_TIME_CHOICES = [
        ("morning", "Morning (8AM - 12PM)"),
        ("afternoon", "Afternoon (12PM - 6PM)"),
        ("evening", "Evening (6PM - 8PM)"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="customer_profile",
        limit_choices_to={"user_type": "customer"},
    )

    # Preferences
    preferred_delivery_time = models.CharField(
        max_length=50,
        choices=DELIVERY_TIME_CHOICES,
        default="morning",
    )

    # Customer statistics
    total_orders = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    loyalty_points = models.IntegerField(default=0)

    # Notifications preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Customer: {self.user.username}"

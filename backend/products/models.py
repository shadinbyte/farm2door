# products/models.py

from accounts.models import FarmerProfile, User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    UNIT_CHOICES = [
        ("kg", "Kilogram"),
        ("piece", "Piece"),
        ("dozen", "Dozen"),
        ("liter", "Liter"),
        ("bunch", "Bunch"),
        ("pack", "Pack"),
    ]

    FRESHNESS_CHOICES = [
        ("fresh", "Fresh (Harvested Today)"),
        ("1day", "1 Day Old"),
        ("2days", "2 Days Old"),
        ("3days", "3 Days Old"),
    ]

    farmer = models.ForeignKey(
        FarmerProfile, on_delete=models.CASCADE, related_name="products"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )

    name = models.CharField(max_length=200)
    description = models.TextField()
    price_per_unit = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="kg")

    # Inventory
    stock_quantity = models.IntegerField(validators=[MinValueValidator(0)])
    minimum_order_quantity = models.IntegerField(
        default=1, validators=[MinValueValidator(1)]
    )
    maximum_order_quantity = models.IntegerField(blank=True, null=True)

    # Product details
    freshness = models.CharField(
        max_length=10, choices=FRESHNESS_CHOICES, default="fresh"
    )
    organic = models.BooleanField(default=False)
    harvest_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)

    # Media
    main_image = models.ImageField(upload_to="products/")

    # Availability
    is_available = models.BooleanField(default=True)
    is_seasonal = models.BooleanField(default=False)
    available_from = models.DateField(blank=True, null=True)
    available_until = models.DateField(blank=True, null=True)

    # Statistics
    total_sold = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.IntegerField(default=0)

    # SEO and search
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category", "is_available"]),
            models.Index(fields=["farmer", "is_available"]),
            models.Index(fields=["price_per_unit"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.farmer.farm_name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify

            base_slug = slugify(f"{self.name}-{self.farmer.farm_name}")
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0 and self.is_available

    @property
    def average_rating(self):
        return self.rating if self.review_count > 0 else 0


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="products/gallery/")
    alt_text = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductReview(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={"user_type": "customer"}
    )

    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField(blank=True)

    # Review verification
    verified_purchase = models.BooleanField(default=False)

    # Moderation
    is_approved = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["product", "customer"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer.username} - {self.product.name} ({self.rating}★)"


class Wishlist(models.Model):
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={"user_type": "customer"}
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["customer", "product"]

    def __str__(self):
        return f"{self.customer.username} - {self.product.name}"

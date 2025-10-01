# products/serializers.py

from accounts.serializers import FarmerProfileSerializer
from django.db.models import Avg
from rest_framework import serializers

from .models import Category, Product, ProductImage, ProductReview, Wishlist


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "description", "image", "is_active", "product_count"]

    def get_product_count(self, obj):
        return obj.products.filter(is_available=True).count()


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "is_featured", "order"]


class ProductReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.username", read_only=True)
    customer_first_name = serializers.CharField(
        source="customer.first_name", read_only=True
    )

    class Meta:
        model = ProductReview
        fields = [
            "id",
            "rating",
            "title",
            "comment",
            "customer_name",
            "customer_first_name",
            "verified_purchase",
            "created_at",
        ]
        read_only_fields = ["customer", "verified_purchase", "is_approved"]


class ProductListSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source="farmer.farm_name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    is_in_stock = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id",
            "slug",
            "name",
            "price_per_unit",
            "unit",
            "main_image",
            "farmer_name",
            "category_name",
            "organic",
            "freshness",
            "is_in_stock",
            "rating",
            "review_count",
            "average_rating",
            "stock_quantity",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    farmer = FarmerProfileSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    is_in_stock = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    is_wishlisted = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "price_per_unit",
            "unit",
            "stock_quantity",
            "minimum_order_quantity",
            "maximum_order_quantity",
            "freshness",
            "organic",
            "harvest_date",
            "expiry_date",
            "main_image",
            "is_available",
            "is_seasonal",
            "available_from",
            "available_until",
            "total_sold",
            "rating",
            "review_count",
            "farmer",
            "category",
            "images",
            "reviews",
            "is_in_stock",
            "average_rating",
            "is_wishlisted",
            "created_at",
            "updated_at",
        ]

    def get_is_wishlisted(self, obj):
        user = self.context["request"].user
        if user.is_authenticated and user.user_type == "customer":
            return Wishlist.objects.filter(customer=user, product=obj).exists()
        return False


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(
            max_length=1000000, allow_empty_file=False, use_url=False
        ),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "category",
            "price_per_unit",
            "unit",
            "stock_quantity",
            "minimum_order_quantity",
            "maximum_order_quantity",
            "freshness",
            "organic",
            "harvest_date",
            "expiry_date",
            "main_image",
            "is_available",
            "is_seasonal",
            "available_from",
            "available_until",
            "images",
            "uploaded_images",
        ]
        read_only_fields = ["farmer"]

    def create(self, validated_data):
        uploaded_images = validated_data.pop("uploaded_images", [])

        # Set farmer from request user
        farmer_profile = self.context["request"].user.farmer_profile
        validated_data["farmer"] = farmer_profile

        product = Product.objects.create(**validated_data)

        # Create product images
        for i, image in enumerate(uploaded_images):
            ProductImage.objects.create(product=product, image=image, order=i)

        return product

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop("uploaded_images", [])

        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Add new images if provided
        if uploaded_images:
            existing_count = instance.images.count()
            for i, image in enumerate(uploaded_images):
                ProductImage.objects.create(
                    product=instance, image=image, order=existing_count + i
                )

        return instance


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "product", "created_at"]
        read_only_fields = ["customer"]


class CreateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ["product", "rating", "title", "comment"]

    def create(self, validated_data):
        validated_data["customer"] = self.context["request"].user
        review = ProductReview.objects.create(**validated_data)

        # Update product rating
        product = review.product
        avg_rating = ProductReview.objects.filter(
            product=product, is_approved=True
        ).aggregate(Avg("rating"))["rating__avg"]

        if avg_rating:
            product.rating = round(avg_rating, 2)
            product.review_count = ProductReview.objects.filter(
                product=product, is_approved=True
            ).count()
            product.save()

        return review

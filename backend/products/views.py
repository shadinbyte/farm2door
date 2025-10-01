# products/views.py

from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .filters import ProductFilter
from .models import Category, Product, ProductReview, Wishlist
from .permissions import IsCustomer, IsFarmerOwner
from .serializers import (
    CategorySerializer,
    CreateReviewSerializer,
    ProductCreateUpdateSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ProductReviewSerializer,
    WishlistSerializer,
)


class CategoryListView(generics.ListAPIView):
    """List all active categories"""

    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ProductListView(generics.ListAPIView):
    """List all available products with filtering and search"""

    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ProductFilter
    search_fields = ["name", "description", "farmer__farm_name"]
    ordering_fields = ["price_per_unit", "rating", "created_at", "total_sold"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Product.objects.filter(
            is_available=True, stock_quantity__gt=0
        ).select_related("farmer", "category")


class ProductDetailView(generics.RetrieveAPIView):
    """Get product details by slug or ID"""

    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        return Product.objects.select_related("farmer", "category").prefetch_related(
            "images", "reviews__customer"
        )


class FarmerProductListView(generics.ListCreateAPIView):
    """List farmer's products or create new product"""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProductCreateUpdateSerializer
        return ProductListSerializer

    def get_queryset(self):
        if self.request.user.user_type == "farmer":
            return Product.objects.filter(
                farmer=self.request.user.farmer_profile
            ).select_related("category")
        return Product.objects.none()

    def perform_create(self, serializer):
        if self.request.user.user_type != "farmer":
            raise permissions.PermissionDenied("Only farmers can create products")
        serializer.save()


class FarmerProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Farmer can view, update or delete their own products"""

    serializer_class = ProductCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmerOwner]
    lookup_field = "slug"

    def get_queryset(self):
        if self.request.user.user_type == "farmer":
            return Product.objects.filter(farmer=self.request.user.farmer_profile)
        return Product.objects.none()


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def toggle_wishlist(request, product_id):
    """Add or remove product from wishlist"""
    if request.user.user_type != "customer":
        return Response(
            {"error": "Only customers can use wishlist"},
            status=status.HTTP_403_FORBIDDEN,
        )

    product = get_object_or_404(Product, id=product_id, is_available=True)
    wishlist_item, created = Wishlist.objects.get_or_create(
        customer=request.user, product=product
    )

    if created:
        return Response(
            {"message": "Product added to wishlist", "wishlisted": True},
            status=status.HTTP_201_CREATED,
        )
    else:
        wishlist_item.delete()
        return Response(
            {"message": "Product removed from wishlist", "wishlisted": False},
            status=status.HTTP_200_OK,
        )


class CustomerWishlistView(generics.ListAPIView):
    """List customer's wishlist"""

    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def get_queryset(self):
        return Wishlist.objects.filter(customer=self.request.user).select_related(
            "product__farmer", "product__category"
        )


class ProductReviewListView(generics.ListCreateAPIView):
    """List product reviews or create new review"""

    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateReviewSerializer
        return ProductReviewSerializer

    def get_queryset(self):
        product_id = self.kwargs["product_id"]
        return ProductReview.objects.filter(
            product_id=product_id, is_approved=True
        ).select_related("customer")

    def perform_create(self, serializer):
        if self.request.user.user_type != "customer":
            raise permissions.PermissionDenied("Only customers can write reviews")

        product_id = self.kwargs["product_id"]
        product = get_object_or_404(Product, id=product_id)

        # Check if customer already reviewed this product
        if ProductReview.objects.filter(
            customer=self.request.user, product=product
        ).exists():
            raise serializers.ValidationError("You have already reviewed this product")

        serializer.save()


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def search_suggestions(request):
    """Get search suggestions based on query"""
    query = request.GET.get("q", "").strip()

    if not query or len(query) < 2:
        return Response({"suggestions": []})

    # Search in product names and farmer names
    products = (
        Product.objects.filter(
            Q(name__icontains=query) | Q(farmer__farm_name__icontains=query),
            is_available=True,
        )
        .values("name", "farmer__farm_name")
        .distinct()[:10]
    )

    suggestions = []
    for product in products:
        suggestions.append(
            {"name": product["name"], "farmer": product["farmer__farm_name"]}
        )

    return Response({"suggestions": suggestions})


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def featured_products(request):
    """Get featured products (highly rated, popular)"""
    featured = (
        Product.objects.filter(is_available=True, stock_quantity__gt=0, rating__gte=4.0)
        .select_related("farmer", "category")
        .order_by("-rating", "-total_sold")[:12]
    )

    serializer = ProductListSerializer(featured, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def farmer_products(request, farmer_id):
    """Get all products from a specific farmer"""
    products = (
        Product.objects.filter(
            farmer_id=farmer_id, is_available=True, stock_quantity__gt=0
        )
        .select_related("category")
        .order_by("-created_at")
    )

    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def category_products(request, category_id):
    """Get all products from a specific category"""
    products = (
        Product.objects.filter(
            category_id=category_id, is_available=True, stock_quantity__gt=0
        )
        .select_related("farmer", "category")
        .order_by("-created_at")
    )

    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)

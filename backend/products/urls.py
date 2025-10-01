# products/urls.py

from django.urls import path

from . import views

urlpatterns = [
    # Categories
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    # Public product views
    path("", views.ProductListView.as_view(), name="product_list"),
    path("<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("farmer/<int:farmer_id>/", views.farmer_products, name="farmer_products"),
    path(
        "category/<int:category_id>/", views.category_products, name="category_products"
    ),
    path("featured/", views.featured_products, name="featured_products"),
    path("search/suggestions/", views.search_suggestions, name="search_suggestions"),
    # Farmer product management
    path(
        "farmer/my-products/",
        views.FarmerProductListView.as_view(),
        name="farmer_products_list",
    ),
    path(
        "farmer/my-products/<slug:slug>/",
        views.FarmerProductDetailView.as_view(),
        name="farmer_product_detail",
    ),
    # Wishlist
    path("wishlist/", views.CustomerWishlistView.as_view(), name="customer_wishlist"),
    path(
        "<int:product_id>/wishlist/toggle/",
        views.toggle_wishlist,
        name="toggle_wishlist",
    ),
    # Reviews
    path(
        "<int:product_id>/reviews/",
        views.ProductReviewListView.as_view(),
        name="product_reviews",
    ),
]

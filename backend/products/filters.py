# products/filters.py

import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    category = django_filters.NumberFilter(field_name="category__id")
    farmer = django_filters.NumberFilter(field_name="farmer__id")
    min_price = django_filters.NumberFilter(
        field_name="price_per_unit", lookup_expr="gte"
    )
    max_price = django_filters.NumberFilter(
        field_name="price_per_unit", lookup_expr="lte"
    )
    organic = django_filters.BooleanFilter()
    freshness = django_filters.ChoiceFilter(choices=Product.FRESHNESS_CHOICES)
    unit = django_filters.ChoiceFilter(choices=Product.UNIT_CHOICES)
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")
    rating_min = django_filters.NumberFilter(field_name="rating", lookup_expr="gte")

    class Meta:
        model = Product
        fields = [
            "name",
            "category",
            "farmer",
            "min_price",
            "max_price",
            "organic",
            "freshness",
            "unit",
            "in_stock",
            "rating_min",
        ]

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock_quantity__gt=0, is_available=True)
        return queryset

# products/permissions.py

from rest_framework import permissions


class IsFarmerOwner(permissions.BasePermission):
    """
    Custom permission to only allow farmers to edit their own products.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == "farmer"

    def has_object_permission(self, request, view, obj):
        # Check if the product belongs to the farmer
        return obj.farmer.user == request.user


class IsCustomer(permissions.BasePermission):
    """
    Custom permission to only allow customers.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == "customer"


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only to the owner
        return obj.customer == request.user

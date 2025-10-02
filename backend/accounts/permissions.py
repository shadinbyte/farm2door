from rest_framework import permissions


class IsFarmer(permissions.BasePermission):
    """
    Permission to only allow farmers to access
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == "farmer"


class IsCustomer(permissions.BasePermission):
    """
    Permission to only allow customers to access
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == "customer"


class IsAdmin(permissions.BasePermission):
    """
    Permission to only allow admins to access
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == "admin"


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners to edit
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only to owner
        return obj.user == request.user

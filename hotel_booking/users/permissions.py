from rest_framework import permissions


class IsCustomer(permissions.BasePermission):
    """
    Custom permission to only allow customers to access their own data.
    """
    
    def has_permission(self, request, view):
        # Allow if user is authenticated and is not a hotel manager
        return request.user.is_authenticated and not hasattr(request.user, 'hotel_manager')
    
    def has_object_permission(self, request, view, obj):
        # Allow if the object belongs to the user
        return obj.user == request.user


class IsHotelManager(permissions.BasePermission):
    """
    Custom permission to only allow hotel managers to access their hotel data.
    """
    
    def has_permission(self, request, view):
        # Allow if user is authenticated and is a hotel manager
        return request.user.is_authenticated and hasattr(request.user, 'hotel_manager')
    
    def has_object_permission(self, request, view, obj):
        # Allow if the object's hotel is managed by the user
        if hasattr(obj, 'hotel'):
            return obj.hotel in request.user.hotel_manager.hotels.all()
        return False
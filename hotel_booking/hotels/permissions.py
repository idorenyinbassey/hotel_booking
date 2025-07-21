from rest_framework import permissions


class IsHotelManagerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow hotel managers to edit hotels.
    """
    
    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS requests
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if user is authenticated
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, OPTIONS requests
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Allow staff users
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Check if user is a manager of this hotel
        if hasattr(request.user, 'hotel') and request.user.hotel == obj:
            return True
        
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, OPTIONS requests
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Allow staff users
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Check if user is the owner of the object
        return obj.user == request.user
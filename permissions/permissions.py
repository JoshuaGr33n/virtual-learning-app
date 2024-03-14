# permissions.py (create this file in your app directory)

from rest_framework.permissions import BasePermission

class IsVerifiedUser(BasePermission):
    """
    Allows access only to verified users.
    """
    from rest_framework.permissions import BasePermission

class IsVerifiedUser(BasePermission):
    """
    Allows access only to verified users.
    """
    
    message = 'Your account is not verified.'

    def has_permission(self, request, view):
        # Check if the user is verified
        verified = bool(request.user and request.user.is_verified)
        if not verified:
            pass
        return verified

class IsAdmin(BasePermission):
    """
    Allows access only to admin and sub-admin.
    """
    
    message = 'Not Allowed'

    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            # User is an admin
            return True
        else:
            # User is not an admin
            return False



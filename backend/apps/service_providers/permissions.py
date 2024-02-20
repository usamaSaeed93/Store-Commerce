from rest_framework.permissions import BasePermission


class IsServiceProvider(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.is_service_provider)

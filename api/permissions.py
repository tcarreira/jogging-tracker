from rest_framework import permissions

from .models import UserRoles


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        # obj is the object found in the database
        return obj.user == request.user


class IsSelfOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if bool(
            request.user
            and (request.user.is_superuser or request.user.role in [UserRoles.ADMIN])
        ):
            return True

        return obj.user == request.user


class IsOwnerOrManager(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if bool(
            request.user
            and (
                request.user.is_superuser
                or request.user.role in [UserRoles.MANAGER, UserRoles.ADMIN]
            )
        ):
            return True

        return obj.user == request.user

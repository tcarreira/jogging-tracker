from rest_framework import permissions

from .models import UserRoles, User


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
            and (
                request.user.is_superuser
                or request.user.role in [r.value for r in [UserRoles.ADMIN]]
            )
        ):
            return True

        return obj == request.user


class IsSelfOrManager(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if bool(
            request.user
            and (
                request.user.is_superuser
                or request.user.role
                in [r.value for r in [UserRoles.ADMIN, UserRoles.MANAGER]]
            )
        ):
            return True

        return obj == request.user


class IsOwnerOrManager(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_permission(self, request, view):
        if "user" in request.data:
            try:
                user = User.objects.get(username=request.data["user"])
                return (
                    user == request.user
                    or request.user.is_superuser
                    or request.user.role
                    in [r.value for r in [UserRoles.MANAGER, UserRoles.ADMIN]]
                )
            except:
                return False
        else:
            return True

    def has_object_permission(self, request, view, obj):
        if bool(
            request.user
            and (
                request.user.is_superuser
                or request.user.role
                in [r.value for r in [UserRoles.MANAGER, UserRoles.ADMIN]]
            )
        ):
            return True

        return obj.user == request.user


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_permission(self, request, view):
        if "user" in request.data:
            try:
                user = User.objects.get(username=request.data["user"])
                return (
                    user == request.user
                    or request.user.is_superuser
                    or request.user.role in [r.value for r in [UserRoles.ADMIN]]
                )
            except:
                return False
        else:
            return True

    def has_object_permission(self, request, view, obj):
        if bool(
            request.user
            and (
                request.user.is_superuser
                or request.user.role in [r.value for r in [UserRoles.ADMIN]]
            )
        ):
            return True

        return obj.user == request.user

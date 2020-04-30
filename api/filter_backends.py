from rest_framework import filters

from .models import UserRoles


class IsSelfOrAdminFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """

    def filter_queryset(self, request, queryset, view):
        if bool(
            request.user
            and (request.user.is_superuser or request.user.role in [UserRoles.ADMIN])
        ):
            return queryset.filter(is_superuser=False)
        return queryset.filter(id=request.user.id)


class IsOwnerOrAdminFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """

    def filter_queryset(self, request, queryset, view):
        if bool(
            request.user
            and (request.user.is_superuser or request.user.role in [UserRoles.ADMIN])
        ):
            return queryset
        return queryset.filter(user=request.user)


class IsOwnerOrManagerFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """

    def filter_queryset(self, request, queryset, view):
        if bool(
            request.user
            and (
                request.user.is_superuser
                or request.user.role in [UserRoles.ADMIN, UserRoles.MANAGER]
            )
        ):
            return queryset
        return queryset.filter(user=request.user)

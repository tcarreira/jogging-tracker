
from advanced_filters.filters import AdvancedFilter

from .models import UserRoles


class IsSelfOrAdminFilterBackend(AdvancedFilter):
    """
    Filter that only allows users to see their own objects.
    """

    def filter_queryset(self, request, queryset, view):
        queryset = super(IsSelfOrAdminFilterBackend, self).filter_queryset(request, queryset, view)

        if bool(
            request.user
            and (request.user.is_superuser or request.user.role in [UserRoles.ADMIN])
        ):
            return queryset.filter(is_superuser=False)
        return queryset.filter(id=request.user.id)


class IsOwnerOrAdminFilterBackend(AdvancedFilter):
    """
    Filter that only allows users to see their own objects.
    """

    def filter_queryset(self, request, queryset, view):
        queryset = super(IsOwnerOrAdminFilterBackend, self).filter_queryset(request, queryset, view)

        if bool(
            request.user
            and (request.user.is_superuser or request.user.role in [UserRoles.ADMIN])
        ):
            return queryset
        return queryset.filter(user=request.user)


class IsOwnerOrManagerFilterBackend(AdvancedFilter):
    """
    Filter that only allows users to see their own objects.
    """

    def filter_queryset(self, request, queryset, view):
        queryset = super(IsOwnerOrManagerFilterBackend, self).filter_queryset(request, queryset, view)
        
        if bool(
            request.user
            and (
                request.user.is_superuser
                or request.user.role in [UserRoles.ADMIN, UserRoles.MANAGER]
            )
        ):
            return queryset
        return queryset.filter(user=request.user)

from rest_framework import filters


class IsOwnerOrAdminFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """

    def filter_queryset(self, request, queryset, view):
        if bool(request.user and request.user.is_staff):
            return queryset
        return queryset.filter(user=request.user)

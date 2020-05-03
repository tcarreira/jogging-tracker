from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.db.models.functions import ExtractWeek, ExtractYear
from django.http import HttpResponse
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filter_backends import (
    IsOwnerOrAdminFilterBackend,
    IsSelfOrAdminFilterBackend,
    IsSelfOrManagerFilterBackend,
)
from .models import Activity, User, UserRoles, Weather
from .permissions import IsOwnerOrAdmin, IsSelfOrAdmin, IsSelfOrManager
from .serializers import (
    ActivityReportSerializer,
    ActivitySerializer,
    UserSerializer,
    WeatherSerializer,
)


# Create your views here.
def hello_world(request):
    return HttpResponse("Hello, world. You're at the polls index.")


class Logout(APIView):
    """Logout a User"""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist, AssertionError):
            pass

        try:
            logout(request)
        except (AttributeError, ObjectDoesNotExist, AssertionError):
            pass

        return Response(status=status.HTTP_200_OK)


class ActivityViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    """
    API endpoint that allows activities to be viewed or edited.

    create:
    Enpoint for creating an Activity 

    retrieve:
    Return an Activity instance

    list:
    Return owned Activities

    update:
    Update Activity instance

    partial:
    Update part of a Activity instance

    destroy:
    Delete Activity instance

    """

    lookup_field = "id"
    queryset = Activity.objects.select_related("user", "weather")
    serializer_class = ActivitySerializer
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin)
    filter_backends = (IsOwnerOrAdminFilterBackend,)


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    """
    API endpoint that allows users to be viewed or edited.

    create:
    Enpoint for creating a User. Returns a User instance 

    retrieve:
    Return a User instance

    list:
    Return all users, ordered by most recently joined

    update:
    Update User instance

    partial:
    Update part of a User instance

    destroy:
    Delete User instance

    """

    lookup_field = "username"
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny, IsSelfOrManager)
    filter_backends = (IsSelfOrManagerFilterBackend,)

    @action(detail=True, methods=["get"], filter_backends=(IsSelfOrAdminFilterBackend,))
    def report(self, request, username=None):
        "Return a report on average speed & distance per week"
        activities_avg_by_week = (
            self.get_object()
            .activities.values("date", "distance", "duration")
            .annotate(year=ExtractYear("date"))
            .annotate(week=ExtractWeek("date"))
            .values("year", "week")
            .annotate(sum_distance=Sum("distance"), sum_duration=Sum("duration"),)
        )

        page = self.paginate_queryset(activities_avg_by_week)
        if page is not None:
            serializer = ActivityReportSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ActivityReportSerializer(activities_avg_by_week, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # check for previlege escalation:
        if (
            "role" in serializer.validated_data
            and serializer.validated_data["role"] < UserRoles.REGULAR.value
            and not request.user.is_superuser
            and (
                not hasattr(request.user, "role")
                or serializer.validated_data["role"] < request.user.role
            )
        ):
            # cannot upgrade to better permissions than self's
            raise PermissionDenied(
                "You do not have permissions for creating a User with role %s"
                % serializer.validated_data["role"]
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # check for previlege escalation:
        if (
            "role" in serializer.validated_data
            and serializer.validated_data["role"] < UserRoles.REGULAR.value
            and not request.user.is_superuser
            and (
                not hasattr(request.user, "role")
                or serializer.validated_data["role"] < request.user.role
            )
        ):
            # cannot upgrade to better permissions than self's
            raise PermissionDenied(
                "You do not have permissions for upgrading user to role %s"
                % serializer.validated_data["role"]
            )

        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class WeatherViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet,
):

    """
    API endpoint that allows Weather to be viewed.

    retrieve:
    Return a Weather instance.

    list:
    Return all Weathers

    """

    lookup_field = "title"
    queryset = Weather.objects.all()
    serializer_class = WeatherSerializer

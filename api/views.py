from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.db.models.functions import ExtractWeek, ExtractYear
from django.http import HttpResponse
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filter_backends import (
    IsOwnerOrAdminFilterBackend,
    IsSelfOrAdminFilterBackend,
    IsSelfOrManagerFilterBackend,
)
from .models import Activity, User, Weather
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
        activities = self.get_object().activities.values("id", "date", "distance")
        activities_avg_by_week = (
            self.get_object()
            .activities.values("date", "distance")
            .annotate(year=ExtractYear("date"))
            .annotate(week=ExtractWeek("date"))
            .values("year", "week")
            .annotate(sum_distance=Sum("distance"))
        )

        page = self.paginate_queryset(activities_avg_by_week)
        if page is not None:
            serializer = ActivityReportSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ActivityReportSerializer(activities_avg_by_week, many=True)
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

from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.db.models.functions import ExtractWeek, ExtractYear
from django.http import HttpResponse
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filter_backends import IsOwnerOrManagerFilterBackend, IsSelfOrAdminFilterBackend
from .models import Activity, User, Weather
from .permissions import IsOwnerOrManager, IsSelfOrAdmin
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
    """Add logout capabilities to rest_framework.authtoken"""

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
    viewsets.GenericViewSet,
):
    lookup_field = "id"
    queryset = Activity.objects.select_related("user", "weather")
    serializer_class = ActivitySerializer
    permission_classes = (IsAuthenticated, IsOwnerOrManager)
    filter_backends = (IsOwnerOrManagerFilterBackend,)


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "username"
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsSelfOrAdmin)
    filter_backends = (IsSelfOrAdminFilterBackend,)

    def create(self, *args, **kwargs):
        response = super(UserViewSet, self).create(self.request, *args, **kwargs)

        if "password" in self.request.data and "username" in response.data:
            user = User.objects.get(username=response.data["username"])
            user.set_password(self.request.data["password"])
            user.save()

        return response

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
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "title"
    queryset = Weather.objects.all()
    serializer_class = WeatherSerializer

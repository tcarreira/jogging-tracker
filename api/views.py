from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filter_backends import IsOwnerOrAdminFilterBackend
from .models import Activity, User, Weather
from .permissions import IsOwnerOrAdmin
from .serializers import ActivitySerializer, UserSerializer, WeatherSerializer


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
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin)
    filter_backends = (IsOwnerOrAdminFilterBackend,)


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

    def create(self, *args, **kwargs):
        response = super(UserViewSet, self).create(self.request, *args, **kwargs)

        if "password" in self.request.data and "username" in response.data:
            user = User.objects.get(username=response.data["username"])
            user.set_password(self.request.data["password"])
            user.save()

        return response


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

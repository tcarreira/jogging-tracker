from django.http import HttpResponse
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Activity, Weather
from .serializers import ActivitySerializer, WeatherSerializer


# Create your views here.
def hello_world(request):
    return HttpResponse("Hello, world. You're at the polls index.")


class Logout(APIView):
    """Add logout capabilities to rest_framework.authtoken"""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class ActivityViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "id"
    queryset = Activity.objects.select_related("user", "weather")
    serializer_class = ActivitySerializer


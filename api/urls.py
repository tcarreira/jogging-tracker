from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.renderers import JSONOpenAPIRenderer
from rest_framework.routers import SimpleRouter
from rest_framework.schemas import get_schema_view

from jogging_tracker import __version__

from . import views

router = SimpleRouter(trailing_slash=False)
router.register("activities", views.ActivityViewSet)
router.register("users", views.UserViewSet)
router.register("weather", views.WeatherViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("auth/login", obtain_auth_token, name="api_auth_token"),
    path("auth/logout", views.Logout.as_view()),
    path(
        "schema.yaml",
        get_schema_view(
            title="Jogging Tracker API",
            description="REST API that tracks jogging times of users",
            version=__version__,
        ),
        name="openapi-schema",
    ),
    path(
        "schema.json",
        get_schema_view(
            title="Jogging Tracker API",
            description="REST API that tracks jogging times of users",
            version=__version__,
            renderer_classes=[JSONOpenAPIRenderer],
        ),
        name="openapi-json-schema",
    ),
]

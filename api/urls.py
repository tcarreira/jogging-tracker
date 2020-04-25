from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter(trailing_slash=False)
router.register("activities", views.ActivityViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("auth/login", obtain_auth_token, name="api_auth_token"),
    path("auth/logout", views.Logout.as_view()),
]

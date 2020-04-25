from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token


from . import views

urlpatterns = [
    path("auth/login", obtain_auth_token, name="api_auth_token"),
    path("auth/logout", views.Logout.as_view()),
    path("activities/", views.hello_world),
]

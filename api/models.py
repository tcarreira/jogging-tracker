from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Meta:
        permissions = [
            ("crud_users", "Can modify any User"),
        ]

    pass


class Activity(models.Model):
    class Meta:
        permissions = [
            ("crud_others_activities", "Can change the any activity (owned by other user)"),
        ]

    date = models.DateTimeField(null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    distance = models.PositiveIntegerField(null=True)
    weather = models.ForeignKey("Weather", on_delete=models.DO_NOTHING)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)


class Weather(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=80, null=True)
    description = models.CharField(max_length=254, null=True)

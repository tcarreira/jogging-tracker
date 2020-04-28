from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Meta:
        permissions = [
            ("crud_users", "Can modify any User"),
        ]


class Activity(models.Model):
    class Meta:
        permissions = [
            ("crud_others_activities", "Can change any activity (owned by other user)"),
        ]

    date = models.DateTimeField(null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
    distance = models.PositiveIntegerField(null=False)
    weather = models.ForeignKey("Weather", null=True, on_delete=models.DO_NOTHING)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)

    def __str__(self):
        return "{}: {} - {}".format(self.user, self.date, self.distance)


class Weather(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=80, null=False)
    description = models.CharField(max_length=254, null=False)

    def __str__(self):
        return self.title

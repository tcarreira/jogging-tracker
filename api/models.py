from typing import Optional

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .external_sources import WeatherProvider


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

    def save(self, *args, **kwargs):
        if self.pk is None and hasattr(self, "latitude") and hasattr(self, "longitude"):
            # on create, get weather
            weather_dict = WeatherProvider().getWeather(
                float(self.latitude), float(self.longitude)
            )
            weather = Weather.get_or_create(**weather_dict)
            self.weather = weather

        elif "form" in kwargs and (
            "latitude" in kwargs["form"].changed_data
            or "longitude" in kwargs["form"].changed_data
        ):
            # if updating lat/lon, the weather info is not valid anymore
            self.weather = None

        super(Activity, self).save(*args, **kwargs)


class Weather(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=80, null=False)
    description = models.CharField(max_length=254, null=False)

    def __str__(self):
        return self.title

    @staticmethod
    def get_or_create(
        id: Optional[int] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional["Weather"]:
        """Create Weather Object is not exists (by id). 
        Returns None if incomplete or no data is provided"""
        if id is None or title is None or description is None:
            return None

        weather, _ = Weather.objects.get_or_create(
            id=id, defaults={"title": title, "description": description}
        )
        return weather

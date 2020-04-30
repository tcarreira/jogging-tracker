from django.conf import settings
from rest_framework import serializers

from .models import Activity, User, Weather


class ActivitySerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field="username"
    )
    weather = serializers.SlugRelatedField(read_only=True, slug_field="title")
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)

    class Meta:
        model = Activity
        fields = (
            "id",
            "date",
            "distance",
            "latitude",
            "longitude",
            "user",
            "weather",
        )

    def to_representation(self, instance):
        representation = super(ActivitySerializer, self).to_representation(instance)

        representation["date"] = instance.date.strftime(settings.API_DATETIME_FORMAT)
        return representation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        fields = (
            "username",
            "first_name",
            "last_name",
            "role",
        )


class WeatherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weather
        fields = (
            "id",
            "title",
            "description",
        )

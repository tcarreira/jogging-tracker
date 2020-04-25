from rest_framework import serializers

from .models import Activity, Weather, User


class ActivitySerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    weather = serializers.SlugRelatedField(queryset=Weather.objects.all(), slug_field="title")

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


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.RelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = "__all__"
        fields = (
            "username",
            "first_name",
            "last_name",
            "groups",
        )


class WeatherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weather
        fields = (
            "id",
            "title",
            "description",
        )

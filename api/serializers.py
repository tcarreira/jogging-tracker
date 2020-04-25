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


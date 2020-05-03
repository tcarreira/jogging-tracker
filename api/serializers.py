from django.conf import settings
from rest_framework import serializers

from .models import Activity, User, Weather, UserRoles


class CustomCurrentUserDefault(dict, serializers.CurrentUserDefault):
    pass


class ActivitySerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        queryset=User.objects.all().filter(is_superuser=False),
        slug_field="username",
        default=CustomCurrentUserDefault(),
    )
    weather = serializers.SlugRelatedField(read_only=True, slug_field="title")
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)

    class Meta:
        model = Activity
        fields = (
            "id",
            "date",
            "time",
            "distance",
            "duration",
            "latitude",
            "longitude",
            "user",
            "weather",
        )


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "role",
        )

    def get_role(self, obj):
        if hasattr(obj, "role"):
            return UserRoles(obj.role).name
        else:
            return UserRoles(obj["role"]).name

    def to_internal_value(self, data):
        validated_data = super(UserSerializer, self).to_internal_value(data)

        if "role" in data:
            if hasattr(UserRoles, data["role"].upper()):
                validated_data["role"] = getattr(UserRoles, data["role"].upper()).value
            else:
                raise serializers.ValidationError(
                    {"role": "%s is not a valid role" % data["role"]}
                )

        if "password" in data:
            validated_data["password"] = data["password"]

        return validated_data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            instance.set_password(validated_data["password"])

        return super(UserSerializer, self).update(instance, validated_data)


class WeatherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weather
        fields = (
            "id",
            "title",
            "description",
        )


class ActivityReportSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    week = serializers.IntegerField()
    average_speed = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()

    def get_distance(self, obj):
        return obj["sum_distance"]

    def get_average_speed(self, obj):
        try:
            return round(obj["sum_distance"] / obj["sum_duration"].total_seconds(), 3)
        except ZeroDivisionError:
            return None

from unittest import mock

from django.test import TestCase
from django.utils import timezone
from rest_framework import status

from api.models import Activity, User, Weather


class TestActivities(TestCase):
    @mock.patch("api.external_sources.WeatherProvider.getWeather")
    def setUp(self, mock_get_weather):
        mock_get_weather.return_value = {
            "id": 1,
            "title": "Clouds",
            "description": "broken clouds",
        }

        users = [
            User.objects.create_user(username="user1", password="123456"),
            User.objects.create_user(username="user2", password="123456"),
            User.objects.create_superuser(
                username="useradmin", email=None, password="123456"
            ),
        ]

        for i, user in enumerate(users):
            for j in range(1, 30):
                Activity.objects.create(
                    date="2020-01-{:02d}T00:01:00Z".format(j),
                    distance=10 * i,
                    user=user,
                    latitude=0,
                    longitude=0,
                )

    def test_report_activities_user1(self):
        self.client.login(username="user1", password="123456")
        response = self.client.get("/api/v1/users/user1/report")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 5)  # 5 weeks
        self.assertDictEqual(
            response.data["results"][0], {"year": 2020, "week": 1, "distance": 0}
        )

    def test_report_activities_wrong_user(self):
        self.client.login(username="user2", password="123456")
        response = self.client.get("/api/v1/users/user1/report")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_report_activities_user2(self):
        self.client.login(username="user2", password="123456")
        response = self.client.get("/api/v1/users/user2/report")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 5)  # 5 weeks
        self.assertDictEqual(
            response.data["results"][0],
            {"year": 2020, "week": 1, "distance": 50},  # this week was only 5 days
        )
        self.assertDictEqual(
            response.data["results"][1], {"year": 2020, "week": 2, "distance": 70}
        )
        self.assertDictEqual(
            response.data["results"][4],
            {"year": 2020, "week": 5, "distance": 30},  # days 27, 28, 29 / jan 2020
        )

    def test_report_activities_admin_can_see_user2(self):
        self.client.login(username="useradmin", password="123456")
        response = self.client.get("/api/v1/users/user2/report")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 5)  # 5 weeks
        self.assertDictEqual(
            response.data["results"][0],
            {"year": 2020, "week": 1, "distance": 50},  # this week was only 5 days
        )
        self.assertDictEqual(
            response.data["results"][1], {"year": 2020, "week": 2, "distance": 70}
        )
        self.assertDictEqual(
            response.data["results"][4],
            {"year": 2020, "week": 5, "distance": 30},  # days 27, 28, 29 / jan 2020
        )

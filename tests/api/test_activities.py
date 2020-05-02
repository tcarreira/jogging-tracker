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
            User.objects.create_user(username="user3", password="123456"),
        ]

        activity_common = {
            "distance": 10,
            "latitude": 20,
            "longitude": 30,
        }

        self.this_now = timezone.now()

        a = Activity.objects.create(
            date=self.this_now, user=users[0], **activity_common,
        )
        Activity.objects.create(
            date=self.this_now, user=users[0], **activity_common,
        )
        Activity.objects.create(
            date=self.this_now, user=users[1], **activity_common,
        )
        Activity.objects.create(
            date=self.this_now, user=users[2], **activity_common,
        )

        # this activity will have weather=None
        mock_get_weather.return_value = None
        Activity.objects.create(
            date=self.this_now, user=users[3], **activity_common,
        )

    def test_get_only_own_activities(self):
        self.assertTrue(self.client.login(username="user1", password="123456"))

        response = self.client.get("/api/v1/activities",)

        self.assertTrue("results" in response.data)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)

    def test_get_activity_with_null_weather(self):
        self.assertTrue(self.client.login(username="user3", password="123456"))

        response = self.client.get("/api/v1/activities",)

        self.assertTrue("results" in response.data)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIsNone(response.data["results"][0]["weather"])

    def test_get_all_activities_from_admin(self):
        self.assertTrue(self.client.login(username="useradmin", password="123456"))

        response = self.client.get("/api/v1/activities",)

        self.assertTrue("results" in response.data)
        self.assertEqual(response.data["count"], 5)
        self.assertEqual(len(response.data["results"]), 5)

    def test_access_to_own_activity(self):
        self.assertTrue(self.client.login(username="user1", password="123456"))

        response = self.client.get("/api/v1/activities/1",)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["distance"], 10)
        self.assertEqual(response.data["latitude"], 20.0)
        self.assertEqual(response.data["longitude"], 30.0)
        self.assertEqual(response.data["weather"], "Clouds")

    def test_access_to_others_activity_not_found(self):
        self.assertTrue(self.client.login(username="user2", password="123456"))

        response = self.client.get("/api/v1/activities/1",)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_access_to_other_activity_from_admin(self):
        self.assertTrue(self.client.login(username="useradmin", password="123456"))

        response = self.client.get("/api/v1/activities/1",)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch("api.external_sources.WeatherProvider.getWeather")
    def test_create_own_activity(self, mock_get_weather):
        mock_get_weather.return_value = {
            "id": 234,
            "title": "SomeClouds",
            "description": "AnotherClouds",
        }

        self.assertTrue(self.client.login(username="user1", password="123456"))

        response = self.client.post(
            "/api/v1/activities",
            {
                "date": "2020-04-29T23:36:53Z",
                "distance": 5,
                "latitude": 15.0,
                "longitude": 16.0,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["distance"], 5)
        self.assertEqual(response.data["latitude"], 15.0)
        self.assertEqual(response.data["longitude"], 16.0)
        self.assertEqual(response.data["weather"], "SomeClouds")
        id = response.data["id"]

        response = self.client.get(f"/api/v1/activities/{id}",)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["distance"], 5)
        self.assertEqual(response.data["latitude"], 15.0)
        self.assertEqual(response.data["longitude"], 16.0)
        self.assertEqual(response.data["weather"], "SomeClouds")

    @mock.patch("api.external_sources.WeatherProvider.getWeather")
    def test_create_others_activity(self, mock_get_weather):
        mock_get_weather.return_value = {
            "id": 234,
            "title": "SomeClouds",
            "description": "AnotherClouds",
        }

        self.assertTrue(self.client.login(username="user1", password="123456"))

        response = self.client.post(
            "/api/v1/activities",
            {
                "date": "2020-04-29T23:36:53Z",
                "distance": 5,
                "latitude": 15.0,
                "longitude": 16.0,
                "user": "user2",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch("api.external_sources.WeatherProvider.getWeather")
    def test_create_others_activity_as_admin(self, mock_get_weather):
        mock_get_weather.return_value = {
            "id": 234,
            "title": "SomeClouds",
            "description": "AnotherClouds",
        }

        self.assertTrue(self.client.login(username="useradmin", password="123456"))

        response = self.client.post(
            "/api/v1/activities",
            {
                "date": "2020-04-29T23:36:53Z",
                "distance": 5,
                "latitude": 15.0,
                "longitude": 16.0,
                "user": "user2",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["distance"], 5)
        self.assertEqual(response.data["latitude"], 15.0)
        self.assertEqual(response.data["longitude"], 16.0)
        self.assertEqual(response.data["weather"], "SomeClouds")
        id = response.data["id"]

        response = self.client.get(f"/api/v1/activities/{id}",)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["distance"], 5)
        self.assertEqual(response.data["latitude"], 15.0)
        self.assertEqual(response.data["longitude"], 16.0)
        self.assertEqual(response.data["weather"], "SomeClouds")

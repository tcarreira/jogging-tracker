from django.test import TestCase
from django.utils import timezone
from rest_framework import status

from api.models import Activity, User, Weather


class TestActivities(TestCase):
    def setUp(self):
        users = [
            User.objects.create_user(username="user1", password="123456"),
            User.objects.create_user(username="user2", password="123456"),
            User.objects.create_superuser(username="useradmin", password="123456"),
        ]

        weather = Weather.objects.create(title="abc", description="abc")

        activity_common = {
            "distance": 1,
            "latitude": 1,
            "longitude": 1,
            "weather": weather,
        }

        self.this_now = timezone.now()

        Activity.objects.create(
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

    def test_get_only_own_activities(self):
        self.assertTrue(self.client.login(username="user1", password="123456"))

        response = self.client.get("/api/v1/activities",)

        self.assertEqual(len(response.data), 2)

    def test_get_all_activities_from_admin(self):
        self.assertTrue(self.client.login(username="useradmin", password="123456"))

        response = self.client.get("/api/v1/activities",)

        self.assertEqual(len(response.data), 4)

    def test_access_to_own_activity(self):
        self.assertTrue(self.client.login(username="user1", password="123456"))

        response = self.client.get("/api/v1/activities/1",)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_to_others_activity_not_found(self):
        self.assertTrue(self.client.login(username="user2", password="123456"))

        response = self.client.get("/api/v1/activities/1",)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_access_to_other_activity_from_admin(self):
        self.assertTrue(self.client.login(username="useradmin", password="123456"))

        response = self.client.get("/api/v1/activities/1",)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

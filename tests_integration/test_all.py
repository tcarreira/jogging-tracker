"Integration tests for testing workflows and all"
from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from rest_framework import status

from api.models import Activity, User, Weather

BASE_API = "/api/v1/"


class TestAll(TestCase):
    "Test specific/complete workflows"

    def setUp(self):
        user = User.objects.create_superuser(username="admin", password="adminpass")

        weather = Weather.objects.create(title="abc", description="abc")
        Activity.objects.create(
            distance=2,
            latitude=2,
            longitude=2,
            date=timezone.now(),
            weather=weather,
            user=user,
        )

    def test_case1(self):
        "test complete flow"
        #####################################################################
        # Login with admin user
        response = self.client.post(
            BASE_API + "auth/login",
            data={"username": "admin", "password": "adminpass"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "token")
        admin_token = response.data["token"]

        #####################################################################
        # Create user without credentials should fail (NOT YET IMPLEMENTED)

        #####################################################################
        # Create new user
        response = self.client.post(
            BASE_API + "users",
            data={"username": "myuser", "password": "supersecurepass"},
            format="json",
            HTTP_AUTHORIZATION="Token {}".format(admin_token),
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        #####################################################################
        # Login as new user:
        response = self.client.post(
            BASE_API + "auth/login",
            data={"username": "myuser", "password": "supersecurepass"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "token")
        myuser_token = response.data["token"]

        ###############################################
        # Add activity (XXX: hard codeded weather for now)
        this_now = timezone.now()
        response = self.client.post(
            BASE_API + "activities",
            data={
                "distance": 2,
                "latitude": 2,
                "longitude": 2,
                "date": this_now,
                "weather": "abc",
                "user": "myuser",
            },
            format="json",
            HTTP_AUTHORIZATION="Token {}".format(myuser_token),
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertDictEqual(
            response.data,
            {
                "id": 2,
                "distance": 2,
                "latitude": "2.000000",
                "longitude": "2.000000",
                "date": this_now.strftime(settings.API_DATETIME_FORMAT),
                "weather": "abc",
                "user": "myuser",
            },
        )

        ###############################################
        # Get user's activities
        this_now = timezone.now()
        response = self.client.get(
            BASE_API + "activities", HTTP_AUTHORIZATION="Token {}".format(myuser_token),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Got Only one result
        self.assertDictEqual(
            dict(response.data[0]),
            {
                "id": 2,
                "distance": 2,
                "latitude": "2.000000",
                "longitude": "2.000000",
                "date": this_now.strftime(settings.API_DATETIME_FORMAT),
                "weather": "abc",
                "user": "myuser",
            },
        )

        ###############################################
        # Get user's activities
        this_now = timezone.now()
        response = self.client.get(
            BASE_API + "activities", HTTP_AUTHORIZATION="Token {}".format(myuser_token),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))

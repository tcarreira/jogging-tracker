from django.test import TestCase

from django.utils import timezone
from rest_framework import status
from api.models import Activity, User, Weather

BASE_API = "/api/v1/"


class TestAll(TestCase):
    def setUp(self):
        user = User.objects.create_superuser(username="admin")
        user.set_password("adminpass")
        user.save()

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
        # myuser_token = response.data["token"]

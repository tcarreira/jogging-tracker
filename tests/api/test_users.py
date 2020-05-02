from django.test import TestCase
from rest_framework import status
from api.models import User, UserRoles


class TestUsers(TestCase):
    def setUp(self):
        User.objects.create_superuser(
            username="useradmin",
            email=None,
            password="123456",
            role=UserRoles.ADMIN.value,
        ),

    def test_superadmin_creates_admin(self):
        self.assertTrue(self.client.login(username="useradmin", password="123456"))

        response = self.client.post(
            "/api/v1/users",
            {
                "username": "user1",
                "password": "123456",
                "first_name": "First",
                "last_name": "Last",
                "role": "admin",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

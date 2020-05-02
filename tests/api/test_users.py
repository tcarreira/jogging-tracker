from django.test import TestCase
from rest_framework import status
from api.models import User, UserRoles


class TestUsers(TestCase):
    def setUp(self):
        for role in UserRoles:
            User.objects.create_user(
                username="user_{}".format(role.name.lower()),
                email=None,
                password="123456",
                role=role.value,
            ),

    def test_admin_creates_admin(self):
        self.assertTrue(self.client.login(username="user_admin", password="123456"))

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
        self.assertDictEqual(
            response.data,
            {
                "username": "user1",
                "first_name": "First",
                "last_name": "Last",
                "role": "ADMIN",
            },
        )

    def test_admin_creates_default_role(self):
        self.assertTrue(self.client.login(username="user_admin", password="123456"))

        response = self.client.post(
            "/api/v1/users",
            {
                "username": "user1",
                "password": "123456",
                "first_name": "First",
                "last_name": "Last",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertDictEqual(
            response.data,
            {
                "username": "user1",
                "first_name": "First",
                "last_name": "Last",
                "role": "REGULAR",
            },
        )

    def test_manager_create_fails(self):
        self.assertTrue(self.client.login(username="user_manager", password="123456"))

        response = self.client.post(
            "/api/v1/users",
            {
                "username": "user1",
                "password": "123456",
                "first_name": "First",
                "last_name": "Last",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_change_role(self):
        self.assertTrue(self.client.login(username="user_regular", password="123456"))

        response = self.client.put(
            "/api/v1/users/user_regular",
            {
                "username": "user_regular",
                "password": "12345678",
                "first_name": "First",
                "last_name": "Last",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

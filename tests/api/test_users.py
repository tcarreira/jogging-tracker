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
            content_type="application/json",
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
            content_type="application/json",
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

    def test_create_no_login(self):

        response = self.client.post(
            "/api/v1/users",
            {
                "username": "user1",
                "password": "123456",
                "first_name": "First",
                "last_name": "Last",
            },
            content_type="application/json",
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

    def test_list_users_no_login(self):
        response = self.client.get("/api/v1/users")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_list_users_some_login(self):
        self.assertTrue(self.client.login(username="user_manager", password="123456"))

        response = self.client.get("/api/v1/users")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_list_users_admin_login(self):
        self.assertTrue(self.client.login(username="user_admin", password="123456"))

        response = self.client.get("/api/v1/users")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_change_own_fields(self):
        self.assertTrue(self.client.login(username="user_regular", password="123456"))

        response = self.client.put(
            "/api/v1/users/user_regular",
            {
                "username": "user_regular",
                "first_name": "Second",
                "last_name": "Lastestss",
                "role": "regular",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get("/api/v1/users/user_regular")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.data,
            {
                "username": "user_regular",
                "first_name": "Second",
                "last_name": "Lastestss",
                "role": "REGULAR",
            },
        )

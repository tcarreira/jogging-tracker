from django.test import TestCase

from rest_framework import status
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.test import APIRequestFactory

from api.models import User
from api.views import Logout


class TestAuthentication(TestCase):
    def setUp(self):
        for username, password in [("admin", "adminpass"), ("user2", "pass2")]:
            user = User.objects.create(username=username)
            user.set_password(password)
            user.save()

    def test_login_and_logout(self):
        factory = APIRequestFactory()
        request = factory.post(
            "/api/v1/login", {"username": "admin", "password": "adminpass"}, format="json"
        )
        response = obtain_auth_token(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

        # Logout this token
        token = response.data["token"]
        request = factory.get("/api/v1/logout", HTTP_AUTHORIZATION="Token {}".format(token))
        view = Logout.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data)

        # Retry same token and fails as unauthorized
        view = Logout.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_wrong_credentials(self):
        factory = APIRequestFactory()
        request = factory.post(
            "/api/v1/login", {"username": "user", "password": "pass"}, format="json"
        )
        response = obtain_auth_token(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

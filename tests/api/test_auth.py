from django.test import TestCase

from rest_framework import status
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.test import APIRequestFactory

from api.models import User


class TestAuthentication(TestCase):
    def setUp(self):
        for username, password in [("admin", "adminpass"), ("user2", "pass2")]:
            user = User.objects.create(username=username)
            user.set_password(password)
            user.save()

    def test_login(self):
        factory = APIRequestFactory()
        request = factory.post(
            "/api/v1/login", {"username": "admin", "password": "adminpass"}, format="json"
        )
        response = obtain_auth_token(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_wrong_credentials(self):
        factory = APIRequestFactory()
        request = factory.post(
            "/api/v1/login", {"username": "user", "password": "pass"}, format="json"
        )
        response = obtain_auth_token(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

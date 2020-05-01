"Integration tests for testing workflows and all"
from unittest import mock

from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from django.utils.http import urlquote_plus
from rest_framework import status

from api.models import Activity, User, Weather

BASE_API = "/api/v1/"


class TestAll(TestCase):
    "Test specific/complete workflows"

    @mock.patch("pyowm.commons.http_client.HttpClient.cacheable_get_json")
    def setUp(self, mock_get_json):

        # Mock external API
        owm_stub_response_json = '{"coord":{"lon":20,"lat":15},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04n"}],"base":"stations","main":{"temp":307.82,"feels_like":302.39,"temp_min":307.82,"temp_max":307.82,"pressure":1006,"humidity":9,"sea_level":1006,"grnd_level":963},"wind":{"speed":4.37,"deg":26},"clouds":{"all":53},"dt":1588101568,"sys":{"country":"TD","sunrise":1588047487,"sunset":1588092991},"timezone":3600,"id":2434508,"name":"Chad","cod":200}'
        mock_get_json.return_value = (None, owm_stub_response_json)

        user = User.objects.create_superuser(
            username="admin", email="", password="adminpass"
        )

        self.nowdate = timezone.now()
        Activity.objects.create(
            distance=20, latitude=30, longitude=40, date=self.nowdate, user=user,
        )

    @mock.patch("pyowm.commons.http_client.HttpClient.cacheable_get_json")
    def test_case1(self, mock_get_json):
        "test complete flow"

        # Mock external API
        owm_stub_response_json = '{"coord":{"lon":20,"lat":15},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04n"}],"base":"stations","main":{"temp":307.82,"feels_like":302.39,"temp_min":307.82,"temp_max":307.82,"pressure":1006,"humidity":9,"sea_level":1006,"grnd_level":963},"wind":{"speed":4.37,"deg":26},"clouds":{"all":53},"dt":1588101568,"sys":{"country":"TD","sunrise":1588047487,"sunset":1588092991},"timezone":3600,"id":2434508,"name":"Chad","cod":200}'
        mock_get_json.return_value = (None, owm_stub_response_json)

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
        # Add activity
        this_now = timezone.now()
        response = self.client.post(
            BASE_API + "activities",
            data={
                "distance": 20,
                "latitude": 30.0,
                "longitude": 40.0,
                "date": this_now,
                "user": "myuser",
            },
            format="json",
            HTTP_AUTHORIZATION="Token {}".format(myuser_token),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Got: " + str(response.content),
        )
        self.assertEqual(response.data["id"], 2)
        self.assertEqual(response.data["distance"], 20)
        self.assertEqual(response.data["latitude"], 30.0)
        self.assertEqual(response.data["longitude"], 40.0)
        self.assertEqual(
            response.data["date"], this_now.strftime(settings.API_DATETIME_FORMAT)
        )
        self.assertEqual(response.data["weather"], "Clouds")
        self.assertEqual(response.data["user"], "myuser")

        ###############################################
        # Get user's activities
        this_now = timezone.now()
        response = self.client.get(
            BASE_API + "activities", HTTP_AUTHORIZATION="Token {}".format(myuser_token),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("results" in response.data)
        self.assertEqual(len(response.data["results"]), 1)  # Got Only one result
        self.assertEqual(response.data["count"], 1)  # Got Only one result
        self.assertDictEqual(
            dict(response.data["results"][0]),
            {
                "id": 2,
                "distance": 20,
                "latitude": 30.0,
                "longitude": 40.0,
                "date": this_now.strftime(settings.API_DATETIME_FORMAT),
                "weather": "Clouds",
                "user": "myuser",
            },
        )


class TestActivityPagination(TestCase):
    @mock.patch("api.external_sources.WeatherProvider.getWeather")
    def test_pagination(self, mock_get_weather):
        mock_get_weather.return_value = {
            "id": 100,
            "title": "SomeWeather",
            "description": "Weeeeaaaaather",
        }

        user = User.objects.create_user(username="myuser", password="xxx")
        results_count = 47
        results_per_page = settings.REST_FRAMEWORK["PAGE_SIZE"]
        for i in range(results_count):
            Activity.objects.create(
                date="2020-01-01T00:01:{:02d}Z".format(i),
                distance=i,
                user=user,
                latitude=0,
                longitude=0,
            )

        self.assertTrue(self.client.login(username="myuser", password="xxx"))

        response = self.client.get("/api/v1/activities",)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), results_per_page)
        self.assertEqual(response.data["count"], results_count)

    @mock.patch("api.external_sources.WeatherProvider.getWeather")
    def test_pagination_page_size(self, mock_get_weather):
        mock_get_weather.return_value = {
            "id": 100,
            "title": "SomeWeather",
            "description": "Weeeeaaaaather",
        }

        user = User.objects.create_user(username="myuser", password="xxx")
        results_count = 50
        results_per_page = 30
        for i in range(results_count):
            Activity.objects.create(
                date="2020-01-01T00:{:02d}:{:02d}Z".format(int(i / 60), i % 60),
                distance=i,
                user=user,
                latitude=0,
                longitude=0,
            )

        self.assertTrue(self.client.login(username="myuser", password="xxx"))

        response = self.client.get(f"/api/v1/activities?limit={results_per_page}",)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), results_per_page)
        self.assertEqual(response.data["count"], results_count)

        response = self.client.get(
            f"/api/v1/activities?limit={results_per_page}&offset=30",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data["results"]), results_count - results_per_page
        )
        self.assertEqual(response.data["count"], results_count)


class TestAdvancedFilters(TestCase):
    @mock.patch("api.external_sources.WeatherProvider.getWeather")
    def setUp(self, mock_get_weather):
        mock_get_weather.return_value = {
            "id": 100,
            "title": "SomeWeather",
            "description": "Weeeeaaaaather",
        }

        user = User.objects.create_user(username="myuser", password="xxx")
        results_count = 50
        results_per_page = 30
        for i in range(results_count):
            Activity.objects.create(
                date="2020-{:02d}-{:02d}T00:{:02d}:{:02d}Z".format(
                    int(i / 27) + 1, (i % 27) + 1, int(i / 60), i % 60
                ),
                distance=i,
                user=user,
                latitude=0,
                longitude=0,
            )

        self.assertTrue(self.client.login(username="myuser", password="xxx"))

    def test_advanced_filters_simple(self):
        response = self.client.get(
            "/api/v1/activities?q=" + urlquote_plus("distance lt 30")
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 30)

    def test_advanced_filters_more_complex(self):
        response = self.client.get(
            "/api/v1/activities?q="
            + urlquote_plus(
                "( (distance lt 30) AND (distance gt 10) ) OR distance gte 45"
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 24)  # 11-29 + 45-49 -> 19+5

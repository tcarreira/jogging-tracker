"Integration tests for testing workflows and all"
import datetime
from unittest import mock

from django.conf import settings
from django.test import TestCase
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
            username="superuser_admin", email="", password="superadminpass"
        )

        self.date = datetime.date(2020, 1, 31)
        self.time = datetime.time(20, 58)

        Activity.objects.create(
            distance=20,
            duration=datetime.timedelta(minutes=1),
            latitude=30,
            longitude=40,
            date=self.date,
            time=self.time,
            user=user,
        )

    @mock.patch("pyowm.commons.http_client.HttpClient.cacheable_get_json")
    def test_case1(self, mock_get_json):
        "test complete flow"

        # Mock external API
        owm_stub_response_json = '{"coord":{"lon":20,"lat":15},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04n"}],"base":"stations","main":{"temp":307.82,"feels_like":302.39,"temp_min":307.82,"temp_max":307.82,"pressure":1006,"humidity":9,"sea_level":1006,"grnd_level":963},"wind":{"speed":4.37,"deg":26},"clouds":{"all":53},"dt":1588101568,"sys":{"country":"TD","sunrise":1588047487,"sunset":1588092991},"timezone":3600,"id":2434508,"name":"Chad","cod":200}'
        mock_get_json.return_value = (None, owm_stub_response_json)

        #####################################################################
        # Create admin user
        response = self.client.post(
            BASE_API + "auth/login",
            data={"username": "superuser_admin", "password": "superadminpass"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "token")
        superadmin_token = response.data["token"]

        #####################################################################
        # Create new admin user
        response = self.client.post(
            BASE_API + "users",
            data={"username": "admin", "password": "adminpass", "role": "admin"},
            content_type="application/json",
            HTTP_AUTHORIZATION="Token {}".format(superadmin_token),
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role"], "ADMIN")

        #####################################################################
        # Login with admin user
        response = self.client.post(
            BASE_API + "auth/login",
            data={"username": "admin", "password": "adminpass"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "token")
        admin_token = response.data["token"]

        #####################################################################
        # Create user without credentials
        response = self.client.post(
            BASE_API + "users",
            data={"username": "myuser", "password": "supersecurepass"},
            content_type="application/json",
            HTTP_AUTHORIZATION="Token {}".format(admin_token),
        )

        #####################################################################
        # Create user without password - fails
        response = self.client.post(
            BASE_API + "users",
            data={"username": "myuser", "password": "supersecurepass"},
            content_type="application/json",
            HTTP_AUTHORIZATION="Token {}".format(admin_token),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
        response = self.client.post(
            BASE_API + "activities",
            data={
                "distance": 20,
                "duration": "01:00",
                "latitude": 30.0,
                "longitude": 40.0,
                "date": "2020-01-31",
                "time": "20:58",
                "user": "myuser",
            },
            content_type="application/json",
            HTTP_AUTHORIZATION="Token {}".format(myuser_token),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Got: " + str(response.content),
        )
        self.assertEqual(response.data["id"], 2)
        self.assertEqual(response.data["distance"], 20)
        self.assertEqual(response.data["duration"], "00:01:00")
        self.assertEqual(response.data["latitude"], 30.0)
        self.assertEqual(response.data["longitude"], 40.0)
        self.assertEqual(response.data["date"], "2020-01-31")
        self.assertEqual(response.data["time"], "20:58:00")
        self.assertEqual(response.data["weather"], "Clouds")
        self.assertEqual(response.data["user"], "myuser")

        ###############################################
        # Get user's activities
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
                "duration": "00:01:00",
                "latitude": 30.0,
                "longitude": 40.0,
                "date": "2020-01-31",
                "time": "20:58:00",
                "weather": "Clouds",
                "user": "myuser",
            },
        )

        ###############################
        # Add 5 activities (for testing report)
        acts = {
            "w15_mon": datetime.date(2019, 4, 8),
            "w15_wed": datetime.date(2019, 4, 10),
            "w15_sun": datetime.date(2019, 4, 14),
            "w16_wed": datetime.date(2019, 4, 17),
        }

        for act in acts.values():
            self.client.post(
                BASE_API + "activities",
                data={
                    "distance": 10,
                    "duration": "01:00",
                    "latitude": 30.0,
                    "longitude": 40.0,
                    "date": act,
                    "time": "20:58",
                    "user": "myuser",
                },
                content_type="application/json",
                HTTP_AUTHORIZATION="Token {}".format(myuser_token),
            )

        ###############################
        # Test Reporting
        response = self.client.get(
            BASE_API + "users/myuser/report",
            HTTP_AUTHORIZATION="Token {}".format(myuser_token),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        self.assertDictEqual(
            response.data["results"][0],
            {"year": 2019, "week": 15, "distance": 30, "average_speed": 0.167},
        )
        self.assertDictEqual(
            response.data["results"][1],
            {"year": 2019, "week": 16, "distance": 10, "average_speed": 0.167},
        )
        self.assertEqual(response.data["results"][2]["distance"], 20)


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
                date=datetime.date(2020, 1, 1),
                time=datetime.time(0, 1, i),
                distance=100 * (i + 1),
                duration=datetime.timedelta(minutes=(i + 1)),
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
                date=datetime.date(2020, 1, 1),
                time=datetime.time(0, int(i / 60), i % 60),
                distance=100 * (i + 1),
                duration=datetime.timedelta(minutes=(i + 1)),
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
                date=datetime.date(2020, int(i / 27) + 1, (i % 27) + 1),
                time=datetime.time(0, int(i / 60), i % 60),
                distance=i,
                duration=datetime.timedelta(minutes=1),
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

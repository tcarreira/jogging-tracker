from unittest import mock

from django.test import TestCase

from api.external_sources import OpenWeatherMapProvider


class TestOpenWeatherMapProvider(TestCase):
    def setUp(self):
        # curl "https://api.openweathermap.org/data/2.5/weather?lat=15&lon=20&lang=en&APPID=xxxxxxxxxxxx"
        self.owm_stub_response_json = '{"coord":{"lon":20,"lat":15},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04n"}],"base":"stations","main":{"temp":307.82,"feels_like":302.39,"temp_min":307.82,"temp_max":307.82,"pressure":1006,"humidity":9,"sea_level":1006,"grnd_level":963},"wind":{"speed":4.37,"deg":26},"clouds":{"all":53},"dt":1588101568,"sys":{"country":"TD","sunrise":1588047487,"sunset":1588092991},"timezone":3600,"id":2434508,"name":"Chad","cod":200}'

    @mock.patch("pyowm.commons.http_client.HttpClient.cacheable_get_json")
    def test_getWeather(self, mock_get_json):
        "this tests the 3rd party lib (on purpose)"
        mock_get_json.return_value = (None, self.owm_stub_response_json)

        result = OpenWeatherMapProvider().getWeather(15, 20, False)
        self.assertDictEqual(
            result, {"id": 803, "title": "Clouds", "description": "broken clouds"}
        )

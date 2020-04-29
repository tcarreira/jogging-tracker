"This handles extracting data from external services / APIs"
import abc
from typing import Optional, TypedDict

import pyowm
from django.conf import settings


class WeatherDict(TypedDict):
    id: int
    title: str
    description: str

    # TypedDict("WeatherDict", {"id": int, "title": str, "description": str})


class AbstractWeatherProvider(abc.ABC):
    "Abstract Weather Provider - interface for supporting another weather providers"

    @abc.abstractmethod
    def getWeather(
        self, lat: float, lon: float, quiet_fail=True
    ) -> Optional[WeatherDict]:
        "get weather or None (if failing to get from API)"
        pass


class OpenWeatherMapProvider(AbstractWeatherProvider):
    def __init__(self):
        self.client = pyowm.OWM(settings.OWM_SECRET, use_ssl=True)

    def getWeather(
        self, lat: float, lon: float, quiet_fail=True
    ) -> Optional[WeatherDict]:
        "get weather or None (if failing to get from API)"

        return_dict = None

        try:
            weather = self.client.weather_at_coords(lat, lon).get_weather()
            return_dict = WeatherDict(
                {
                    "id": int(weather.get_weather_code()),
                    "title": str(weather.get_status()),
                    "description": str(weather.get_detailed_status()),
                }
            )
        except Exception as e:  # pylint: disable=broad-except
            if not quiet_fail:
                raise e

        return return_dict


class WeatherProvider(OpenWeatherMapProvider):
    pass

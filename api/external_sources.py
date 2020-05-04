"This handles extracting data from external services / APIs"
import abc
import logging
from typing import Optional, TypedDict
import datetime
import pyowm
from django.conf import settings

logger = logging.getLogger(__name__)


class WeatherDict(TypedDict):
    id: int
    title: str
    description: str

    # TypedDict("WeatherDict", {"id": int, "title": str, "description": str})


class AbstractWeatherProvider(abc.ABC):
    "Abstract Weather Provider - interface for supporting another weather providers"

    @abc.abstractmethod
    def getWeather(
        self, lat: float, lon: float, when: datetime.datetime = None, quiet_fail=True
    ) -> Optional[WeatherDict]:
        "get weather or None (if failing to get from API)"
        pass


class OpenWeatherMapProvider(AbstractWeatherProvider):
    def __init__(self):
        self.client = pyowm.OWM(
            # settings.OWM_SECRET, use_ssl=True, subscription_type="pro"
            settings.OWM_SECRET,
            use_ssl=True,
            subscription_type="free",  # XXX: until I have a pro account for testing this
        )

    def getWeather(
        self, lat: float, lon: float, when: datetime.datetime = None, quiet_fail=True
    ) -> Optional[WeatherDict]:
        "get weather or None (if failing to get from API)"

        return_dict = None

        try:
            # XXX: until I have a pro account for testing this
            # if when is None:
            if True:
                weather = self.client.weather_at_coords(lat, lon).get_weather()
                return_dict = WeatherDict(
                    {
                        "id": int(weather.get_weather_code()),
                        "title": str(weather.get_status()),
                        "description": str(weather.get_detailed_status()),
                    }
                )
            else:
                weather = self.client.weather_history_at_coords(lat, lon, start=when)
                return_dict = WeatherDict(
                    {
                        "id": int(weather.get_weather_code()),
                        "title": str(weather.get_status()),
                        "description": str(weather.get_detailed_status()),
                    }
                )

        except Exception as e:  # pylint: disable=broad-except
            logging.error("Got exception from OpenWeatherMapProvider: %s", str(e))
            if not quiet_fail:
                raise e

        return return_dict


class WeatherProvider(OpenWeatherMapProvider):
    pass

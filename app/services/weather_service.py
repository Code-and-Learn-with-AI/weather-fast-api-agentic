import httpx

from app.schemas.weather import WeatherResponse
from app.services.openweather import get_current_weather


class WeatherService:
    def __init__(self, client: httpx.AsyncClient, api_key: str) -> None:
        self._client = client
        self._api_key = api_key

    async def get_weather(self, city: str) -> WeatherResponse:
        return await get_current_weather(city=city, api_key=self._api_key, client=self._client)

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from app.schemas.weather import WeatherResponse
from app.services.openweather import get_current_weather

if TYPE_CHECKING:
    from app.repositories.weather_repo import WeatherRepo


class WeatherService:
    def __init__(self, client: httpx.AsyncClient, api_key: str, repo: WeatherRepo | None = None) -> None:
        self._client = client
        self._api_key = api_key
        self._repo = repo

    async def get_weather(self, city: str) -> WeatherResponse:
        response = await get_current_weather(city=city, api_key=self._api_key, client=self._client)
        if self._repo is not None:
            await self._repo.save(response)
        return response

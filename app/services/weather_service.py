from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import httpx

from app.schemas.weather import WeatherResponse
from app.services.openweather import get_current_weather

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from app.repositories.weather_repo import WeatherRepo
    from app.services.cache import WeatherCache


class WeatherService:
    def __init__(
        self,
        client: httpx.AsyncClient,
        api_key: str,
        repo: WeatherRepo | None = None,
        cache: WeatherCache | None = None,
    ) -> None:
        self._client = client
        self._api_key = api_key
        self._repo = repo
        self._cache = cache

    async def get_weather(self, city: str) -> WeatherResponse:
        if self._cache is not None:
            cached = await self._cache.get(city)
            if cached is not None:
                logger.info("Weather fetched from cache for city: %s", city)
                return cached.model_copy(update={"source": "cache"})
        response = await get_current_weather(city=city, api_key=self._api_key, client=self._client)
        response = response.model_copy(update={"source": "api"})
        if self._cache is not None:
            await self._cache.set(city, response)
        if self._repo is not None:
            await self._repo.save(response)
        return response

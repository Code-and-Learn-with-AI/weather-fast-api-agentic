from collections.abc import AsyncGenerator

import httpx
from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.database import get_db_session
from app.repositories.weather_repo import WeatherRepo
from app.schemas.weather import WeatherResponse
from app.services.cache import WeatherCache
from app.services.exceptions import CityNotFoundError, WeatherServiceError
from app.services.weather_service import WeatherService

router = APIRouter()


def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


def get_weather_repo(session: AsyncSession = Depends(get_db_session)) -> WeatherRepo:
    return WeatherRepo(session)


async def get_redis(settings: Settings = Depends(get_settings)) -> AsyncGenerator[Redis]:  # type: ignore[type-arg]
    async with Redis.from_url(settings.REDIS_URL) as client:
        yield client


def get_weather_cache(redis: Redis = Depends(get_redis)) -> WeatherCache:  # type: ignore[type-arg]
    return WeatherCache(redis)


async def get_weather_service(
    settings: Settings = Depends(get_settings),
    repo: WeatherRepo = Depends(get_weather_repo),
    cache: WeatherCache = Depends(get_weather_cache),
) -> AsyncGenerator[WeatherService]:
    async with httpx.AsyncClient() as client:
        yield WeatherService(client=client, api_key=settings.OPENWEATHER_API_KEY, repo=repo, cache=cache)


@router.get("/weather", response_model=WeatherResponse)
async def get_weather(
    city: str,
    service: WeatherService = Depends(get_weather_service),
) -> WeatherResponse:
    try:
        return await service.get_weather(city)
    except CityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WeatherServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

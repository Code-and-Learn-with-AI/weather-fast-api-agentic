from collections.abc import AsyncGenerator

import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.core.config import Settings
from app.schemas.weather import WeatherResponse
from app.services.exceptions import CityNotFoundError, WeatherServiceError
from app.services.weather_service import WeatherService

router = APIRouter()


def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


async def get_weather_service(
    settings: Settings = Depends(get_settings),
) -> AsyncGenerator[WeatherService]:
    async with httpx.AsyncClient() as client:
        yield WeatherService(client=client, api_key=settings.OPENWEATHER_API_KEY)


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

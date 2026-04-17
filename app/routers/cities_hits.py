from fastapi import APIRouter, Depends

from app.repositories.weather_repo import WeatherRepo, get_weather_repo
from app.schemas.cities_hits import (
    CitiesCloudResponse,
    CitiesDotsResponse,
    CityHit,
    DateRangeRequest,
    DotEntry,
)

router = APIRouter()


@router.post("/cities-cloud", response_model=CitiesCloudResponse)
async def cities_cloud(
    body: DateRangeRequest,
    repo: WeatherRepo = Depends(get_weather_repo),
) -> CitiesCloudResponse:
    data = await repo.get_cities_cloud(body.from_dt, body.to_dt)
    return CitiesCloudResponse(cities=[CityHit(city=city, hits=hits) for city, hits in data])


@router.post("/cities-dots", response_model=CitiesDotsResponse)
async def cities_dots(
    body: DateRangeRequest,
    repo: WeatherRepo = Depends(get_weather_repo),
) -> CitiesDotsResponse:
    rows = await repo.get_cities_dots(body.from_dt, body.to_dt)
    return CitiesDotsResponse(dots=[DotEntry(datetime=queried_at, city=city) for city, queried_at in rows])

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.repositories.weather_repo import WeatherRepo
from app.schemas.cities_hits import (
    CitiesCloudResponse,
    CitiesDotsResponse,
    CityHit,
    DateRangeRequest,
    DotEntry,
)

router = APIRouter()


def get_weather_repo(session: AsyncSession = Depends(get_db_session)) -> WeatherRepo:
    return WeatherRepo(session)


@router.post("/cities-cloud", response_model=CitiesCloudResponse)
async def cities_cloud(
    body: DateRangeRequest,
    repo: WeatherRepo = Depends(get_weather_repo),
) -> CitiesCloudResponse:
    data = await repo.get_cities_cloud(body.from_dt, body.to_dt)
    return CitiesCloudResponse(cities=[CityHit(city=city, hits=hits) for city, hits in data.items()])


@router.post("/cities-dots", response_model=CitiesDotsResponse)
async def cities_dots(
    body: DateRangeRequest,
    repo: WeatherRepo = Depends(get_weather_repo),
) -> CitiesDotsResponse:
    rows = await repo.get_cities_dots(body.from_dt, body.to_dt)
    return CitiesDotsResponse(dots=[DotEntry(datetime=row.queried_at, city=row.city) for row in rows])

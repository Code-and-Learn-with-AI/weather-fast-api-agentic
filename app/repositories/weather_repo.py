from datetime import UTC, datetime

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.weather_query import WeatherQuery
from app.schemas.weather import WeatherResponse


def get_weather_repo(session: AsyncSession = Depends(get_db_session)) -> "WeatherRepo":
    return WeatherRepo(session)


class WeatherRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_cities_cloud(self, from_dt: datetime, to_dt: datetime) -> list[tuple[str, int]]:
        result = await self._session.execute(
            select(WeatherQuery.city, func.count(WeatherQuery.id).label("hits"))
            .where(WeatherQuery.queried_at >= from_dt, WeatherQuery.queried_at <= to_dt)
            .group_by(WeatherQuery.city)
        )
        return [(str(row.city), int(row.hits)) for row in result]

    async def get_cities_dots(self, from_dt: datetime, to_dt: datetime) -> list[tuple[str, datetime]]:
        result = await self._session.execute(
            select(WeatherQuery.city, WeatherQuery.queried_at)
            .where(WeatherQuery.queried_at >= from_dt, WeatherQuery.queried_at <= to_dt)
            .order_by(WeatherQuery.queried_at)
        )
        return [(str(row.city), row.queried_at) for row in result]

    async def save(self, response: WeatherResponse) -> WeatherQuery:
        record = WeatherQuery(
            city=response.city,
            country=response.country,
            temperature=response.temperature,
            feels_like=response.feels_like,
            humidity=response.humidity,
            description=response.description,
            icon=response.icon,
            queried_at=datetime.now(UTC),
        )
        self._session.add(record)
        await self._session.commit()
        await self._session.refresh(record)  # refresh the record to get the latest version
        return record

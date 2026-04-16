from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.weather_query import WeatherQuery
from app.schemas.weather import WeatherResponse


class WeatherRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

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
        await self._session.refresh(record)
        return record

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.weather_repo import WeatherRepo
from app.schemas.weather import WeatherResponse

WEATHER_RESPONSE = WeatherResponse(
    city="Paris",
    country="FR",
    temperature=18.5,
    feels_like=17.0,
    humidity=65,
    description="clear sky",
    icon="01d",
)


async def test_save_persists_weather_query(db_session: AsyncSession) -> None:
    repo = WeatherRepo(db_session)
    record = await repo.save(WEATHER_RESPONSE)
    assert record.id is not None
    assert record.city == "Paris"
    assert record.queried_at <= datetime.now(UTC)

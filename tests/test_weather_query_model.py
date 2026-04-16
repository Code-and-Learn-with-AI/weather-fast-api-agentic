import uuid
from datetime import UTC, datetime

from app.models.weather_query import WeatherQuery


def test_weather_query_model() -> None:
    now = datetime.now(UTC)
    record = WeatherQuery(
        id=uuid.uuid4(),
        city="Paris",
        country="FR",
        temperature=18.5,
        feels_like=17.0,
        humidity=65,
        description="clear sky",
        icon="01d",
        queried_at=now,
    )
    assert record.city == "Paris"
    assert record.country == "FR"
    assert record.temperature == 18.5
    assert record.queried_at == now
    assert WeatherQuery.__tablename__ == "weather_queries"

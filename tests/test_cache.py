from collections.abc import AsyncGenerator

import pytest
from fakeredis.aioredis import FakeRedis

from app.schemas.weather import WeatherResponse
from app.services.cache import WeatherCache

WEATHER_RESPONSE = WeatherResponse(
    city="Paris",
    country="FR",
    temperature=18.5,
    feels_like=17.0,
    humidity=65,
    description="clear sky",
    icon="01d",
)


@pytest.fixture
async def fake_redis() -> AsyncGenerator[FakeRedis]:
    async with FakeRedis() as fake_redis_client:
        yield fake_redis_client


async def test_cache_miss_returns_none(fake_redis: FakeRedis) -> None:
    cache = WeatherCache(fake_redis)
    assert await cache.get("Paris") is None


async def test_cache_set_then_get_returns_response(fake_redis: FakeRedis) -> None:
    cache = WeatherCache(fake_redis)
    await cache.set("Paris", WEATHER_RESPONSE)
    result = await cache.get("Paris")
    assert result == WEATHER_RESPONSE


async def test_cache_key_is_case_insensitive(fake_redis: FakeRedis) -> None:
    cache = WeatherCache(fake_redis)
    await cache.set("Paris", WEATHER_RESPONSE)
    assert await cache.get("paris") == WEATHER_RESPONSE
    assert await cache.get("PARIS") == WEATHER_RESPONSE

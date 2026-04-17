from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.weather_query import WeatherQuery


@pytest.fixture
async def paris_query(db_session: AsyncSession) -> WeatherQuery:
    record = WeatherQuery(
        city="Paris",
        country="FR",
        temperature=18.5,
        feels_like=17.0,
        humidity=65,
        description="clear sky",
        icon="01d",
        queried_at=datetime.now(UTC),
    )
    db_session.add(record)
    await db_session.commit()
    await db_session.refresh(record)
    return record


@pytest.mark.usefixtures("paris_query")
async def test_cities_cloud_includes_paris_after_query(db_async_client: AsyncClient) -> None:
    now = datetime.now(UTC)
    payload = {
        "from": (now - timedelta(hours=1)).isoformat(),
        "to": (now + timedelta(hours=1)).isoformat(),
    }
    response = await db_async_client.post("/cities-cloud", json=payload)
    assert response.status_code == 200
    data = response.json()
    cities = {entry["city"]: entry["hits"] for entry in data["cities"]}
    assert "Paris" in cities
    assert cities["Paris"] >= 1


@pytest.mark.usefixtures("paris_query")
async def test_cities_dots_includes_paris_after_query(db_async_client: AsyncClient) -> None:
    now = datetime.now(UTC)
    payload = {
        "from": (now - timedelta(hours=1)).isoformat(),
        "to": (now + timedelta(hours=1)).isoformat(),
    }
    response = await db_async_client.post("/cities-dots", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "dots" in data
    cities = [dot["city"] for dot in data["dots"]]
    assert "Paris" in cities


@pytest.mark.usefixtures("paris_query")
async def test_cities_cloud_excludes_queries_outside_range(db_async_client: AsyncClient) -> None:
    future = datetime.now(UTC) + timedelta(hours=2)
    payload = {
        "from": future.isoformat(),
        "to": (future + timedelta(hours=1)).isoformat(),
    }
    response = await db_async_client.post("/cities-cloud", json=payload)
    assert response.status_code == 200
    assert response.json() == {"cities": []}


@pytest.mark.usefixtures("paris_query")
async def test_cities_dots_excludes_queries_outside_range(db_async_client: AsyncClient) -> None:
    future = datetime.now(UTC) + timedelta(hours=2)
    payload = {
        "from": future.isoformat(),
        "to": (future + timedelta(hours=1)).isoformat(),
    }
    response = await db_async_client.post("/cities-dots", json=payload)
    assert response.status_code == 200
    assert response.json() == {"dots": []}


@pytest.mark.usefixtures("paris_query")
async def test_cities_dots_entry_has_datetime_and_city_fields(db_async_client: AsyncClient) -> None:
    now = datetime.now(UTC)
    payload = {
        "from": (now - timedelta(hours=1)).isoformat(),
        "to": (now + timedelta(hours=1)).isoformat(),
    }
    response = await db_async_client.post("/cities-dots", json=payload)
    assert response.status_code == 200
    dots = response.json()["dots"]
    assert len(dots) >= 1
    assert "datetime" in dots[0]
    assert "city" in dots[0]

import httpx
import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from app.schemas.weather import WeatherResponse
from app.services.exceptions import CityNotFoundError, WeatherServiceError
from app.services.weather_service import WeatherService

_BASE_WEATHER = WeatherResponse(
    city="Paris",
    country="FR",
    temperature=18.5,
    feels_like=17.0,
    humidity=65,
    description="clear sky",
    icon="01d",
)


async def test_weather_response_contains_source_field(
    async_client: AsyncClient, mocker: MockerFixture
) -> None:
    mocker.patch("app.routers.weather.WeatherService.get_weather", return_value=_BASE_WEATHER)
    response = await async_client.get("/weather", params={"city": "Paris"})
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Paris"
    assert "temperature" in data
    assert "source" in data


async def test_cache_hit_returns_source_cache_via_router(
    async_client: AsyncClient, mocker: MockerFixture
) -> None:
    cached_response = _BASE_WEATHER.model_copy(update={"source": "cache"})
    mocker.patch("app.routers.weather.WeatherService.get_weather", return_value=cached_response)
    response = await async_client.get("/weather", params={"city": "Paris"})
    assert response.status_code == 200
    assert response.json()["source"] == "cache"


async def test_cache_hit_sets_source_on_service_response(mocker: MockerFixture) -> None:
    mock_cache = mocker.AsyncMock()
    cached = _BASE_WEATHER.model_copy(update={"source": "cache"})
    mock_cache.get.return_value = cached
    service = WeatherService(
        client=mocker.AsyncMock(spec=httpx.AsyncClient),
        api_key="test-key",
        cache=mock_cache,
    )
    result = await service.get_weather("Paris")
    assert result.source == "cache"  # type: ignore[attr-defined]


async def test_cache_miss_returns_source_api_via_router(
    async_client: AsyncClient, mocker: MockerFixture
) -> None:
    api_response = _BASE_WEATHER.model_copy(update={"source": "api"})
    mocker.patch("app.routers.weather.WeatherService.get_weather", return_value=api_response)
    response = await async_client.get("/weather", params={"city": "Paris"})
    assert response.status_code == 200
    assert response.json()["source"] == "api"


async def test_cache_miss_sets_source_on_service_response(mocker: MockerFixture) -> None:
    mock_cache = mocker.AsyncMock()
    mock_cache.get.return_value = None
    api_response = _BASE_WEATHER.model_copy(update={"source": "api"})
    mocker.patch("app.services.weather_service.get_current_weather", return_value=api_response)
    service = WeatherService(
        client=mocker.AsyncMock(spec=httpx.AsyncClient),
        api_key="test-key",
        cache=mock_cache,
    )
    result = await service.get_weather("Paris")
    assert result.source == "api"  # type: ignore[attr-defined]


async def test_second_request_for_same_city_hits_cache(mocker: MockerFixture) -> None:
    api_response = _BASE_WEATHER.model_copy(update={"source": "api"})
    cached_response = _BASE_WEATHER.model_copy(update={"source": "cache"})
    mock_cache = mocker.AsyncMock()
    mock_cache.get.side_effect = [None, cached_response]
    mocker.patch("app.services.weather_service.get_current_weather", return_value=api_response)
    service = WeatherService(
        client=mocker.AsyncMock(spec=httpx.AsyncClient),
        api_key="test-key",
        cache=mock_cache,
    )
    first = await service.get_weather("Paris")
    second = await service.get_weather("Paris")
    assert first.source == "api"  # type: ignore[attr-defined]
    assert second.source == "cache"  # type: ignore[attr-defined]


async def test_second_request_for_same_city_hits_cache_via_router(
    async_client: AsyncClient, mocker: MockerFixture
) -> None:
    api_response = _BASE_WEATHER.model_copy(update={"source": "api"})
    cached_response = _BASE_WEATHER.model_copy(update={"source": "cache"})
    get_weather_mock = mocker.patch(
        "app.routers.weather.WeatherService.get_weather",
        side_effect=[api_response, cached_response],
    )
    first = await async_client.get("/weather", params={"city": "Paris"})
    second = await async_client.get("/weather", params={"city": "Paris"})
    assert first.json()["source"] == "api"
    assert second.json()["source"] == "cache"
    assert get_weather_mock.call_count == 2


async def test_city_not_found_returns_404(
    async_client: AsyncClient, mocker: MockerFixture
) -> None:
    mocker.patch(
        "app.routers.weather.WeatherService.get_weather",
        side_effect=CityNotFoundError("City 'Atlantis' not found."),
    )
    response = await async_client.get("/weather", params={"city": "Atlantis"})
    assert response.status_code == 404
    assert "Atlantis" in response.json()["detail"]


async def test_upstream_error_returns_502(
    async_client: AsyncClient, mocker: MockerFixture
) -> None:
    mocker.patch(
        "app.routers.weather.WeatherService.get_weather",
        side_effect=WeatherServiceError("upstream failure"),
    )
    response = await async_client.get("/weather", params={"city": "Paris"})
    assert response.status_code == 502
    assert "upstream failure" in response.json()["detail"]


async def test_error_response_does_not_contain_source(
    async_client: AsyncClient, mocker: MockerFixture
) -> None:
    mocker.patch(
        "app.routers.weather.WeatherService.get_weather",
        side_effect=CityNotFoundError("City 'Nowhere' not found."),
    )
    response = await async_client.get("/weather", params={"city": "Nowhere"})
    assert response.status_code == 404
    body = response.json()
    assert "detail" in body
    assert "source" not in body


@pytest.mark.parametrize("city", ["", "   "])
async def test_empty_or_whitespace_city_does_not_crash(
    async_client: AsyncClient, mocker: MockerFixture, city: str
) -> None:
    mocker.patch(
        "app.routers.weather.WeatherService.get_weather",
        side_effect=CityNotFoundError(f"City '{city}' not found."),
    )
    response = await async_client.get("/weather", params={"city": city})
    assert response.status_code in {404, 422}

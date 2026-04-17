import httpx
import pytest
from pytest_mock import MockerFixture

from app.schemas.weather import WeatherResponse
from app.services.exceptions import CityNotFoundError, WeatherServiceError
from app.services.weather_service import WeatherService

WEATHER_RESPONSE = WeatherResponse(
    city="Paris",
    country="FR",
    temperature=18.5,
    feels_like=17.0,
    humidity=65,
    description="clear sky",
    icon="01d",
)


async def test_get_weather_returns_weather_response(mocker: MockerFixture) -> None:
    mocker.patch(
        "app.services.weather_service.get_current_weather",
        return_value=WEATHER_RESPONSE,
    )
    service = WeatherService(client=mocker.AsyncMock(spec=httpx.AsyncClient), api_key="test-key")
    result = await service.get_weather("Paris")
    assert result == WEATHER_RESPONSE


async def test_get_weather_saves_to_repo(mocker: MockerFixture) -> None:
    mocker.patch("app.services.weather_service.get_current_weather", return_value=WEATHER_RESPONSE)
    mock_repo = mocker.AsyncMock()
    service = WeatherService(client=mocker.AsyncMock(spec=httpx.AsyncClient), api_key="test-key", repo=mock_repo)
    result = await service.get_weather("Paris")
    mock_repo.save.assert_called_once_with(WEATHER_RESPONSE)
    assert result == WEATHER_RESPONSE


async def test_get_weather_returns_cached_response(mocker: MockerFixture) -> None:
    mock_cache = mocker.AsyncMock()
    mock_cache.get.return_value = WEATHER_RESPONSE
    service = WeatherService(client=mocker.AsyncMock(spec=httpx.AsyncClient), api_key="test-key", cache=mock_cache)
    result = await service.get_weather("Paris")
    mock_cache.get.assert_called_once_with("Paris")
    assert result == WEATHER_RESPONSE


async def test_get_weather_cache_miss_calls_openweather_and_sets_cache(mocker: MockerFixture) -> None:
    mock_cache = mocker.AsyncMock()
    mock_cache.get.return_value = None
    mocker.patch("app.services.weather_service.get_current_weather", return_value=WEATHER_RESPONSE)
    service = WeatherService(client=mocker.AsyncMock(spec=httpx.AsyncClient), api_key="test-key", cache=mock_cache)
    result = await service.get_weather("Paris")
    mock_cache.set.assert_called_once_with("Paris", WEATHER_RESPONSE)
    assert result == WEATHER_RESPONSE


async def test_get_weather_propagates_city_not_found_error(mocker: MockerFixture) -> None:
    mocker.patch(
        "app.services.weather_service.get_current_weather",
        side_effect=CityNotFoundError("City 'Nowhere' not found."),
    )
    service = WeatherService(client=mocker.AsyncMock(spec=httpx.AsyncClient), api_key="test-key")
    with pytest.raises(CityNotFoundError):
        await service.get_weather("Nowhere")


async def test_get_weather_propagates_weather_service_error(mocker: MockerFixture) -> None:
    mocker.patch(
        "app.services.weather_service.get_current_weather",
        side_effect=WeatherServiceError("upstream failure"),
    )
    service = WeatherService(client=mocker.AsyncMock(spec=httpx.AsyncClient), api_key="test-key")
    with pytest.raises(WeatherServiceError):
        await service.get_weather("Paris")

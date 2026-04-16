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

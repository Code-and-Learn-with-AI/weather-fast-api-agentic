import httpx
import pytest
from pytest_mock import MockerFixture

from app.schemas.weather import WeatherResponse
from app.services.exceptions import CityNotFoundError, WeatherServiceError
from app.services.openweather import get_current_weather

OPENWEATHER_RESPONSE = {
    "name": "Paris",
    "sys": {"country": "FR"},
    "main": {"temp": 18.5, "feels_like": 17.0, "humidity": 65},
    "weather": [{"description": "clear sky", "icon": "01d"}],
}


async def test_successful_response_returns_weather_response(mocker: MockerFixture) -> None:
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = OPENWEATHER_RESPONSE

    mock_client = mocker.AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_response

    result = await get_current_weather(city="Paris", api_key="test-key", client=mock_client)

    assert isinstance(result, WeatherResponse)
    assert result.city == "Paris"
    assert result.country == "FR"
    assert result.temperature == 18.5
    assert result.feels_like == 17.0
    assert result.humidity == 65
    assert result.description == "clear sky"
    assert result.icon == "01d"


async def test_404_raises_city_not_found_error(mocker: MockerFixture) -> None:
    mock_response = mocker.MagicMock()
    mock_response.status_code = 404

    mock_client = mocker.AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_response

    with pytest.raises(CityNotFoundError):
        await get_current_weather(city="Nowhere", api_key="test-key", client=mock_client)


async def test_500_raises_weather_service_error(mocker: MockerFixture) -> None:
    mock_response = mocker.MagicMock()
    mock_response.status_code = 500

    mock_client = mocker.AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_response

    with pytest.raises(WeatherServiceError):
        await get_current_weather(city="Paris", api_key="test-key", client=mock_client)


async def test_timeout_raises_weather_service_error(mocker: MockerFixture) -> None:
    mock_client = mocker.AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.side_effect = httpx.TimeoutException("timeout")

    with pytest.raises(WeatherServiceError):
        await get_current_weather(city="Paris", api_key="test-key", client=mock_client)

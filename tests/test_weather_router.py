from httpx import AsyncClient
from pytest_mock import MockerFixture

from app.schemas.weather import WeatherResponse
from app.services.exceptions import CityNotFoundError, WeatherServiceError

WEATHER_RESPONSE = WeatherResponse(
    city="Paris",
    country="FR",
    temperature=18.5,
    feels_like=17.0,
    humidity=65,
    description="clear sky",
    icon="01d",
)


async def test_get_weather_returns_200(async_client: AsyncClient, mocker: MockerFixture) -> None:
    mocker.patch(
        "app.routers.weather.WeatherService.get_weather",
        return_value=WEATHER_RESPONSE,
    )
    response = await async_client.get("/weather", params={"city": "Paris"})
    assert response.status_code == 200
    assert response.json()["city"] == "Paris"


async def test_get_weather_missing_city_returns_422(async_client: AsyncClient) -> None:
    response = await async_client.get("/weather")
    assert response.status_code == 422


async def test_get_weather_city_not_found_returns_404(
    async_client: AsyncClient, mocker: MockerFixture
) -> None:
    mocker.patch(
        "app.routers.weather.WeatherService.get_weather",
        side_effect=CityNotFoundError("City 'Nowhere' not found."),
    )
    response = await async_client.get("/weather", params={"city": "Nowhere"})
    assert response.status_code == 404
    assert "Nowhere" in response.json()["detail"]


async def test_get_weather_upstream_error_returns_502(
    async_client: AsyncClient, mocker: MockerFixture
) -> None:
    mocker.patch(
        "app.routers.weather.WeatherService.get_weather",
        side_effect=WeatherServiceError("upstream failure"),
    )
    response = await async_client.get("/weather", params={"city": "Paris"})
    assert response.status_code == 502
    assert "upstream failure" in response.json()["detail"]

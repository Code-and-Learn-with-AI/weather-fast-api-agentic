import httpx

from app.schemas.weather import WeatherResponse
from app.services.exceptions import CityNotFoundError, WeatherServiceError

_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


async def get_current_weather(
    city: str,
    api_key: str,
    client: httpx.AsyncClient,
) -> WeatherResponse:
    try:
        response = await client.get(
            _BASE_URL,
            params={"q": city, "appid": api_key, "units": "metric"},
        )
    except httpx.TimeoutException as exc:
        raise WeatherServiceError("Request to OpenWeather timed out.") from exc

    if response.status_code == 404:
        raise CityNotFoundError(f"City '{city}' not found.")
    if response.status_code != 200:
        raise WeatherServiceError(f"OpenWeather returned status {response.status_code}.")

    data = response.json()
    return WeatherResponse(
        city=data["name"],
        country=data["sys"]["country"],
        temperature=data["main"]["temp"],
        feels_like=data["main"]["feels_like"],
        humidity=data["main"]["humidity"],
        description=data["weather"][0]["description"],
        icon=data["weather"][0]["icon"],
    )

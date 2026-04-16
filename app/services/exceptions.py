class CityNotFoundError(Exception):
    """Raised when the city is not found by the OpenWeather API."""


class WeatherServiceError(Exception):
    """Raised when the OpenWeather API returns an unexpected error or times out."""

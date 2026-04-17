import pytest
from pydantic import ValidationError

from app.schemas.weather import WeatherResponse


def make_payload(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "city": "Paris",
        "country": "FR",
        "temperature": 18.5,
        "feels_like": 17.0,
        "humidity": 65,
        "description": "clear sky",
        "icon": "01d",
    }
    return {**base, **overrides}


def test_valid_payload_instantiates() -> None:
    weather = WeatherResponse.model_validate(make_payload())
    assert weather.city == "Paris"
    assert weather.country == "FR"
    assert weather.temperature == 18.5
    assert weather.feels_like == 17.0
    assert weather.humidity == 65
    assert weather.description == "clear sky"
    assert weather.icon == "01d"


def test_missing_required_field_raises() -> None:
    payload = make_payload()
    del payload["city"]
    with pytest.raises(ValidationError):
        WeatherResponse.model_validate(payload)


def test_humidity_below_zero_raises() -> None:
    with pytest.raises(ValidationError):
        WeatherResponse.model_validate(make_payload(humidity=-1))


def test_humidity_above_100_raises() -> None:
    with pytest.raises(ValidationError):
        WeatherResponse.model_validate(make_payload(humidity=101))


def test_schema_serializes_to_dict() -> None:
    weather = WeatherResponse.model_validate(make_payload())
    data = weather.model_dump()
    assert set(data.keys()) == {
        "city",
        "country",
        "temperature",
        "feels_like",
        "humidity",
        "description",
        "icon",
        "source",
    }

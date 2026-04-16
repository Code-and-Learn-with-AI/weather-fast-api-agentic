from pydantic import BaseModel, Field


class WeatherResponse(BaseModel):
    city: str
    country: str
    temperature: float
    feels_like: float
    humidity: int = Field(ge=0, le=100)
    description: str
    icon: str

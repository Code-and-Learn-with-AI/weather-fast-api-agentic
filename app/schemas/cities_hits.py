from datetime import datetime

from pydantic import BaseModel, Field


class DateRangeRequest(BaseModel):
    from_dt: datetime = Field(alias="from")
    to_dt: datetime = Field(alias="to")

    model_config = {"populate_by_name": True}


class CityHit(BaseModel):
    city: str
    hits: int


class CitiesCloudResponse(BaseModel):
    cities: list[CityHit]


class DotEntry(BaseModel):
    datetime: datetime
    city: str


class CitiesDotsResponse(BaseModel):
    dots: list[DotEntry]

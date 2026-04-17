from redis.asyncio import Redis

from app.schemas.weather import WeatherResponse

_TTL = 300  # 5 minutes


class WeatherCache:
    def __init__(self, client: Redis) -> None:  # type: ignore[type-arg]
        self._client = client

    def _key(self, city: str) -> str:
        return f"weather:{city.lower()}"

    async def get(self, city: str) -> WeatherResponse | None:
        data = await self._client.get(self._key(city))
        if data is None:
            return None
        return WeatherResponse.model_validate_json(data)

    async def set(self, city: str, response: WeatherResponse) -> None:
        await self._client.set(self._key(city), response.model_dump_json(), ex=_TTL)

import uuid

from httpx import AsyncClient


async def test_middleware_adds_request_id_header(async_client: AsyncClient) -> None:
    response = await async_client.get("/health")
    assert "x-request-id" in response.headers


async def test_middleware_generates_uuid_when_none_provided(async_client: AsyncClient) -> None:
    response = await async_client.get("/health")
    request_id = response.headers["x-request-id"]
    uuid.UUID(request_id)  # raises if not a valid UUID


async def test_middleware_echoes_provided_request_id(async_client: AsyncClient) -> None:
    custom_id = str(uuid.uuid4())
    response = await async_client.get("/health", headers={"x-request-id": custom_id})
    assert response.headers["x-request-id"] == custom_id

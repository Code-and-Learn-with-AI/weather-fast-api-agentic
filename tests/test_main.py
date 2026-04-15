from fastapi import FastAPI
from httpx import AsyncClient

from app.main import app


def test_app_is_fastapi_instance() -> None:
    assert isinstance(app, FastAPI)


async def test_openapi_schema_served(async_client: AsyncClient) -> None:
    response = await async_client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] is not None


async def test_docs_served(async_client: AsyncClient) -> None:
    response = await async_client.get("/docs")
    assert response.status_code == 200

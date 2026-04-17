import uuid

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.routers import cities_hits, weather

app = FastAPI(
    title="Weather FastAPI",
    description="Weather query API backed by OpenWeather.",
    version="0.1.0",
)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response


app.add_middleware(RequestIDMiddleware)

app.include_router(weather.router)
app.include_router(cities_hits.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
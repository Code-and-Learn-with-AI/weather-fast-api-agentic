from fastapi import FastAPI

app = FastAPI(
    title="Weather FastAPI",
    description="Weather query API backed by OpenWeather.",
    version="0.1.0",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
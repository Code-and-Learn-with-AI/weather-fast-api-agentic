from fastapi import FastAPI

app = FastAPI(
    title="Weather FastAPI",
    description="Weather query API backed by OpenWeather.",
    version="0.1.0",
)
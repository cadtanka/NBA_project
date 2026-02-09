from fastapi import FastAPI
from app.routes import games

app = FastAPI(title="NBA Tracking API")

app.include_router(games.router, prefix="/games", tags=["games"])
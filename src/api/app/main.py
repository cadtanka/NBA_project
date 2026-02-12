from fastapi import FastAPI, Request, HTTPException
from src.api.app.routes import games
from src.api.app.cache import r

app = FastAPI(title="NBA Tracking API")

@app.middleware("http")
async def rate_limt(request: Request, call_next):
    ip = request.client.host
    key = f"rate:{ip}"
    count = r.incr(key)

    if count == 1:
        r.expire(key, 60)
    
    if count > 60:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    return await call_next(request)


app.include_router(games.router, prefix="/games", tags=["games"])

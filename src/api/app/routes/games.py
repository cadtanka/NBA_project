from fastapi import APIRouter, UploadFile, BackgroundTasks, HTTPException
from app.models import GameMetaData
from app.db import create_game_entry, get_game_by_id
from app.utils import process_video
from app.cache import cache_get, cache_set

router = APIRouter()

# POST: Process new game video
@router.post("/process")
async def process_game(file: UploadFile, background_tasks: BackgroundTasks):
    game_id = create_game_entry(file.filename)
    background_tasks.add_task(process_video, game_id, file.file)
    return {"game_id": game_id, "status": "processing"}

# GET: Retrieve game metadata
@router.get("/{game_id}", response_model=GameMetaData)
def get_game(game_id: int):
    key = f"game:{game_id}"
    cached = cache_get(key)
    if cached:
        return cached
    
    game = get_game_by_id(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    cache_set(key, game)
    return game
from fastapi import APIRouter, UploadFile, BackgroundTasks, HTTPException, Query
from src.api.app.models import GameMetaData
from src.data.schema import get_games, get_positions_in_timerange
from src.api.app.utils import compute_metrics
from src.api.app.services.track_player import process_video
from src.api.app.cache import cache_get, cache_set
from src.api.app.services.heatmap_service import get_player_heatmap, get_team_heatmap
from src.api.app.services import video_config
from src.api.app.services.video_config import create_default_config
from src.data.analytics_queries import get_movement_vs_performance

router = APIRouter()

# POST: Process new game video
@router.post("/process")
async def process_game(video_path: str, background_tasks: BackgroundTasks):
    config = create_default_config()
    background_tasks.add_task(process_video, video_path, config)
    return {"status": "processing started"}

# GET: Retrieve game metadata
@router.get("/{game_id}", response_model=GameMetaData)
def get_game(game_id: int):
    key = f"game:{game_id}"
    cached = cache_get(key)
    if cached:
        return cached
    
    game = get_games(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    cache_set(key, game, expire=3600)
    return game

# Get positions of players
@router.get("/{game_id}/positions")
def get_positions(game_id: int, start_time: float, end_time: float):
    key = f"positions:{game_id}:{start_time}:{end_time}"
    cached = cache_get(key)
    if cached:
        return cached
    
    positions = get_positions_in_timerange(game_id, start_time, end_time)
    cache_set(key, positions, expire=600)
    return positions 

# Get the metrics of a game
@router.get("/{game_id}/metrics")
def get_metrics(game_id: int):
    key = f"metrics:{game_id}"
    cached = cache_get(key)
    if cached:
        return cached
    
    metrics = compute_metrics(game_id)
    cache_set(key, metrics, expire=3600)
    return metrics

# Get the heatmap
@router.get("/{game_id}/heatmap")
def heatmap_endpoint(
    game_id: int,
    player_id: int = Query(None),
    team: str = Query(None)
):
    
    if not player_id and not team:
        raise HTTPException(status_code=400, detail="Must provide player_id or team")
    
    if player_id:
        cache_key = f"heatmap:{game_id}:{player_id}"

        cached = cache_get(cache_key)
        if cached:
            return cached
        
        result = get_player_heatmap(game_id, player_id)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        cache_set(cache_key, result, expire=3600)

        return result
    
    if team:
        cache_key = f"heatmap:game:{game_id}:team:{team}"
        cached = cache_get(cache_key)
        if cached:
            return cached
        
        result = get_team_heatmap(game_id, team)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        cache_set(cache_key, result, expire=3600)
        return result
    
@router.get("players/{player_id}/movement-vs-performance")
def movement_vs_performance(player_id: int):
    data = get_movement_vs_performance(player_id)
    return {
        "player_id": player_id,
        "games": data
    }
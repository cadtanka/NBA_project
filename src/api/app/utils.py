import time
from collections import defaultdict
import math
from sqlalchemy import text
from src.data.db_entrypoint import engine
from src.data.schema import get_full_tracking

"""
def process_video(game_id: int, file_path: str):
    # Simulate heavy processing
    print(f"Processing video for game {game_id}...")
    time.sleep(5)

    # After processing, update the DB
    from src.api.app.db import games_db
    games_db[game_id]["status"] = "completed"
    games_db[game_id]["teams"] = ["Lakers", "Warriors"]
    print(f"Processing complete for game {game_id}")
"""

def compute_heatmap(game_id: int, player_id: int):
    data = get_full_tracking(game_id)
    heatmap = defaultdict(int)

    for p in data:
        if p["player_id"] == player_id:
            grid_x = int(p["x"] // 5)
            grid_y = int(p["y"] // 5)
            heatmap[(grid_x, grid_y)] += 1

    return [{"grid": k, "count": v} for k,v in heatmap.items()]

def compute_metrics(game_id: int):
    data = get_full_tracking(game_id)

    distances = defaultdict(float)
    prev = {}

    for row in data:
        pid = row["player_id"]
        if pid in prev:
            dx = row["cx"] - prev[pid]["cx"]
            dy = row["cy"] - prev[pid]["cy"]
            distances[pid] += math.sqrt(dx*dx + dy*dy)

        prev[pid] = row

    return {"distance_per_player": distances}

def get_game(game_id: int):
    query = text("""
        SELECT id as game_id, game_date, home_team, away_team, video_path
        FROM games
        WHERE id = :game_id;
    """)

    with engine.begin() as conn:
        result = conn.execute(query, {"game_id":game_id}).mappings().fetchone()

    return dict(result) if result else None

def get_positions_range(game_id: int, start_time: float, end_time: float):
    query = text("""
        SELECT
            f.game_clock,
            f.frame_number,
            p.id as player_id,
            p.team,
            pp.cx,
            pp.cy,
            pp.zone
        FROM frames f 
        JOIN player_positions pp ON pp.frame_id = f.id
        JOIN players p ON pp.player_id = p.id
        WHERE f.game_id = :game_id
        AND f.game_clock BETWEEN :start AND :end
        ORDER BY f.game_clock;
    """)

    with engine.begin() as conn:
        rows = conn.execute(query, {
            "game_id": game_id,
            "start": start_time,
            "end": end_time
        }).mappings().all()

    return [dict(r) for r in rows]
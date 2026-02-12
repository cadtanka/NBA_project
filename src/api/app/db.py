"""
from datetime import date
import random

games_db = {}
positions_db = {}

def create_game_entry(filename: str) -> int:
    game_id = len(games_db) + 1
    games_db[game_id] = {
        "game_id": game_id,
        "status": "processing",
        "teams": [],
        "date": date,
        "filename": filename
    }

    # generate fake tracking data for demo
    positions_db[game_id] = [
        {
            "player_id": random.randint(1,10),
            "x": random.uniform(0, 94),
            "y": random.uniform(0, 50),
            "timestamp": t
        }
        for t in range(0, 600)
    ]

    return game_id

def get_game_by_id(game_id: int):
    return games_db.get(game_id)

def get_positions_range(game_id: int, start: float, end: float):
    data = positions_db.get(game_id, [])
    return [p for p in data if start <= p["timestamp"] <= end]
"""
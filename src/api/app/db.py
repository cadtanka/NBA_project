from datetime import date

games_db = "postgresql://localhost/nba_tracking"

def create_game_entry(filename: str) -> int:
    game_id = len(games_db) + 1
    games_db[game_id] = {
        "game_id": game_id,
        "status": "processing",
        "teams": [],
        "date": date,
        "filename": filename
    }

    return game_id

def get_game_by_id(game_id: int):
    return games_db.get(game_id)

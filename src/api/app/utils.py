import time

def process_video(game_id: int, file_path: str):
    # Simulate heavy processing
    print(f"Processing video for game {game_id}...")
    time.sleep(5)

    # After processing, update the DB
    from app.db import games_db
    games_db[game_id]["status"] = "completed"
    games_db[game_id]["teams"] = ["Lakers", "Warriors"]
    print(f"Processing complete for game {game_id}")
import cv2
import numpy as np
from scipy.ndimage import gaussian_filter
from src.data.schema import get_full_tracking
from scipy.ndimage import gaussian_filter

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
COURT_IMAGE_PATH = "/Users/cadetanaka/Desktop/Other projects/NBA_game_analyzer/src/analysis/images/court_image.png"

court_img = cv2.imread(COURT_IMAGE_PATH)
court_img = cv2.cvtColor(court_img, cv2.COLOR_BGR2RGB)
COURT_H, COURT_W, _ = court_img.shape

def transform_to_court_coords(rows):
    transformed = []

    for r in rows:
        court_x = r["cx"] / VIDEO_WIDTH * COURT_W
        court_y = COURT_H - (r["cy"] / VIDEO_HEIGHT * COURT_H)

        transformed.append({
            "player_id": r["player_id"],
            "team": r["team"],
            "court_x": court_x,
            "court_y": court_y
        })

    return transformed

def generate_heatmap_grid(points, bins=80):
    x = [p["court_x"] for p in points]
    y = [p["court_y"] for p in points]

    heatmap, xedges, yedges = np.histogram2d(x, y, bins=bins)
    heatmap = gaussian_filter(heatmap, sigma=2)

    return heatmap.tolist()

def get_player_heatmap(game_id: int, player_id: int):
    rows = get_full_tracking(game_id)
    rows = transform_to_court_coords(rows)

    player_points = [r for r in rows if r["player_id"] == player_id]

    if len(player_points) < 50:
        return {"error": "Not enough tracking data"}

    heatmap = generate_heatmap_grid(player_points)

    return {
        "player_id": player_id,
        "heatmap": heatmap
    }

def get_team_heatmap(game_id: int, team_name: str):
    rows = get_full_tracking(game_id)
    rows = transform_to_court_coords(rows)

    team_points = [r for r in rows if r["team"] == team_name]

    if len(team_points) < 50:
        return {"error": "Not enough tracking data for team"}

    heatmap = generate_heatmap_grid(team_points)

    return {
        "team": team_name,
        "heatmap": heatmap
    }
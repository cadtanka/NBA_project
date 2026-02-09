import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cv2
from src.data.schema import get_tracking_dataframe
from scipy.ndimage import gaussian_filter

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
COURT_IMAGE_PATH = "/Users/cadetanaka/Desktop/Other projects/NBA_game_analyzer/src/analysis/images/court_image.png"
GAME_ID = 4
df = get_tracking_dataframe(GAME_ID)

court_img = cv2.imread(COURT_IMAGE_PATH)
court_img = cv2.cvtColor(court_img, cv2.COLOR_BGR2RGB)

court_h, court_w, _ = court_img.shape

video_w = VIDEO_WIDTH
video_h = VIDEO_HEIGHT

df["court_x"] = df["cx"] / video_w * court_w
df["court_y"] = court_h - (df["cy"] / video_h * court_h)

def create_court_heatmap(x, y, title, output_file, bins=80):
    heatmap, xedges, yedges = np.histogram2d(x, y, bins=bins)
    heatmap = gaussian_filter(heatmap, sigma=2)

    plt.figure(figsize=(12, 7))

    # draw court first
    plt.imshow(court_img)

    # draw heatmap ON TOP
    plt.imshow(
        heatmap.T,
        extent=[0, court_w, 0, court_h],
        origin="lower",
        alpha=0.6
    )

    plt.title(title)
    plt.axis("off")

    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

# =========================
# TEAM HEATMAPS
# =========================
teams = df["team"].unique()

for team in teams:
    if team == "unknown":
        continue

    team_df = df[df["team"] == team]

    create_court_heatmap(
        team_df["court_x"],
        team_df["court_y"],
        f"{team} Player Position Heatmap",
        f"{team}_game_{GAME_ID}_heatmap.png"
    )

print("Team heatmaps saved.")

# =========================
# PLAYER HEATMAPS
# =========================
players = df["track_id"].unique()
for player in players:
    player_df = df[df["track_id"] == player]

    print(player_df)

    if len(player_df) < 100:
        continue

    create_court_heatmap(
        player_df["court_x"],
        player_df["court_y"],
        f"Player {player} Heatmap",
        f"player_{player}_game_{GAME_ID}_heatmap.png"
    )

print("Player heatmaps saved.")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cv2

CSV_PATH = "/Users/cadetanaka/Desktop/Other projects/NBA_game_analyzer/src/tracking/tracking_data.csv"
COURT_IMAGE_PATH = "/Users/cadetanaka/Desktop/Other projects/NBA_game_analyzer/src/analysis/images/court_image.png"
df = pd.read_csv(CSV_PATH)

court_img = cv2.imread(COURT_IMAGE_PATH)
court_img = cv2.cvtColor(court_img, cv2.COLOR_BGR2RGB)

court_h, court_w, _ = court_img.shape

video_w = df["cx"].max()
video_h = df["cy"].max()

df["court_x"] = df["cx"] / video_w * court_w
df["court_y"] = df["cy"] / video_h * court_h

def create_court_heatmap(x, y, title, output_file, bins=80):
    heatmap, xedges, yedges = np.histogram2d(x, y, bins=bins)

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
        team_df["cx"],
        team_df["cy"],
        f"{team} Player Position Heatmap",
        f"{team}_heatmap.png"
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
        player_df["cx"],
        player_df["cy"],
        f"Player {player} Heatmap",
        f"player_{player}_heatmap.png"
    )

print("Player heatmaps saved.")
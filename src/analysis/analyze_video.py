import pandas as pd
import numpy as np
from src.data.schema import get_tracking_dataframe

FPS = 30
SECONDS_PER_FRAME = 1 / FPS
GAME_ID = 4

df = get_tracking_dataframe(GAME_ID)

print(df.head(), len(df))

df = df.sort_values(["track_id", "frame"]).reset_index(drop=True)

df["time"] = df["frame"] * SECONDS_PER_FRAME

# For each player, compute movement between frames
df["prev_cx"] = df.groupby("track_id")["cx"].shift(1)
df["prev_cy"] = df.groupby("track_id")["cy"].shift(1)
df["prev_time"] = df.groupby("track_id")["time"].shift(1)

# Distance moved between frames
df["dx"] = df["cx"] - df["prev_cx"]
df["dy"] = df["cy"] - df["prev_cy"]
df["dt"] = df["time"] - df["prev_time"]

# Pixel distance per frame -> pixels per second
df["distance"] = np.sqrt(df["dx"]**2 + df["dy"]**2)
df["speed_pixels_per_sec"] = df["distance"] / df["dt"]

# Remove first frame of each track
df = df.dropna(subset=["speed_pixels_per_sec"])

# =========================
# DISTANCE TRAVELED PER PLAYER
# =========================
distance_stats = (
    df.groupby("track_id")["distance"]
    .sum()
    .reset_index(name="total_distance_pixels")
)

# =========================
# TIME SPENT IN ZONES
# =========================
# Compute how log each row lasted
df["time_delta"]  = df.groupby("track_id")["time"].diff()
df["time_delta"] = df["time_delta"].fillna(SECONDS_PER_FRAME)

zone_time = (
    df.groupby(["track_id", "zone"])["time_delta"]
    .sum()
    .reset_index()
)

zone_time_pivot = zone_time.pivot(
    index="track_id",
    columns="zone",
    values="time_delta"
).fillna(0)

# =========================
# AVERAGE SPEED PER PLAYER
# =========================
speed_stats = (
    df.groupby("track_id")["speed_pixels_per_sec"]
    .mean()
    .reset_index(name="avg_speed_pixels_per_sec")
)

# =========================
# TEAM AGGREGATES
# =========================
team_zone_time = (
    df.groupby(["team", "zone"])["time_delta"]
    .sum()
    .reset_index()
)

team_speed = (
    df.groupby("team")["speed_pixels_per_sec"]
    .mean()
    .reset_index(name = "team_avg_speed")
)

# =========================
# SAVE OUTPUTS
# =========================
distance_stats.to_csv(f"player_distance_game_{GAME_ID}.csv", index=False)
speed_stats.to_csv(f"player_speed_game_{GAME_ID}.csv", index=False)
zone_time_pivot.to_csv(f"player_zone_time_game_{GAME_ID}.csv")
team_zone_time.to_csv(f"team_zone_time_game_{GAME_ID}.csv", index=False)
team_speed.to_csv(f"team_speed_game_{GAME_ID}.csv", index=False)

print("Analysis complete!")
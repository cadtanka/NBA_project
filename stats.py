from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.endpoints import PlayerGameLog
from nba_api.stats.endpoints import LeagueGameLog
import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv
import os
import time
import requests.exceptions
import matplotlib.pyplot as plt
from tqdm import tqdm

load_dotenv()
NOAA_TOKEN = os.getenv("API_KEY")
file_path = 'games.csv'
CACHE_FILE = 'games_with_weather.csv'

if os.path.exists(CACHE_FILE):
    print("Loading cached data from file...")
    games_df = pd.read_csv(CACHE_FILE)
else:
    print("No cache found. Fetching data (this will take a while)...")
    
    # Fetch games from NBA API
    games = LeagueGameLog(season='2024-25')
    games_df = games.get_data_frames()[0]
    
    arena_df = pd.read_csv(file_path)
    
    station_cache = {}
    
    def get_nearby_station(lat, lon, retries=3):
        params = {
            "datasetid": "GHCND",
            "extent": f"{lat-0.5},{lon-0.5},{lat+0.5},{lon+0.5}",
            "limit": 10
        }
        for attempt in range(retries):
            print("in get nearby stations")
            try:
                r = requests.get(
                    "https://www.ncei.noaa.gov/cdo-web/api/v2/stations",
                    headers={"token": NOAA_TOKEN},
                    params=params,
                    timeout=10
                )
    
                if r.status_code != 200:
                    return None
    
                try:
                    data = r.json()
                except ValueError:
                    return None
    
                results = data.get("results", [])
                if not results:
                    return None
    
                return results[0]["id"]
    
            except (requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError):
                time.sleep(2 ** attempt)
    
    def get_nearby_station_cached(lat, lon):
        key = (round(lat, 3), round(lon, 3))
        if key not in station_cache:
            station_cache[key] = get_nearby_station(lat, lon)
        return station_cache[key]
    
    arena_df["station_id"] = arena_df.apply(
        lambda r: get_nearby_station_cached(r["lat"], r["lon"]),
        axis=1
    )
    
    games_df = games_df.merge(
        arena_df, 
        left_on='TEAM_ID',
        right_on='team_id',
        how='left'
    )
    
    games_df["GAME_DATE"] = pd.to_datetime(games_df["GAME_DATE"]).dt.strftime("%Y-%m-%d")
    
    def get_weather(station_id, date, retries=3):
        if pd.isna(station_id):
            return None
    
        params = {
            "datasetid": "GHCND",
            "stationid": station_id,
            "startdate": date,
            "enddate": date,
            "units": "standard"
        }
    
        for attempt in range(retries):
            print("in get weather")
            try:
                r = requests.get(
                    "https://www.ncei.noaa.gov/cdo-web/api/v2/data",
                    headers={"token": NOAA_TOKEN},
                    params=params,
                    timeout=10
                )
    
                if r.status_code != 200:
                    return None
    
                try:
                    data = r.json()
                except ValueError:
                    return None
                
                results = data.get("results", [])
                if not results:
                    return None
                
                weather = {row["datatype"]: row["value"] for row in results}
    
                return {
                    "tmin": weather.get("TMIN"),
                    "tmax": weather.get("TMAX"),
                    "prcp": weather.get("PRCP")
                }
            except (requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError):
                time.sleep(2 ** attempt)
    
        return None
    
    def safe_get_weather(row):
        if pd.isna(row["station_id"]):
            return pd.Series([None, None, None])
        
        time.sleep(0.25)
    
        w = get_weather(row["station_id"], row["GAME_DATE"])
        if w is None:
            return pd.Series([None, None, None])
        
        return pd.Series([w["tmin"], w["tmax"], w["prcp"]])
    
    tqdm.pandas(desc="Fetching weather data")
    games_df[["tmin", "tmax", "prcp"]] = games_df.progress_apply(safe_get_weather, axis=1)
    
    # Save the data
    games_df.to_csv(CACHE_FILE, index=False)
    print(f"Data saved to {CACHE_FILE}")

# Plotting (runs whether cached or fresh)
df_plot = games_df.dropna(subset=["tmax", "PTS"])

plt.figure()
plt.scatter(df_plot["tmax"], df_plot["PTS"])
plt.xlabel("Daily Max Temperature (°F)")
plt.ylabel("Points Scored")
plt.title("Game Performance vs Temperature")
plt.show()
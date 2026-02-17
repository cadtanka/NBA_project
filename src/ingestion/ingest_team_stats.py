#python3 -m src.ingestion.ingest_team_stats

from nba_api.stats.endpoints import boxscoreadvancedv2
from nba_api.stats.library.http import NBAStatsHTTP
from sqlalchemy import text
from src.data.db_entrypoint import engine
from requests.exceptions import ReadTimeout
import time
import random
from nba_api.stats.endpoints import boxscoretraditionalv3

import random

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

NBAStatsHTTP.headers = {
    "Host": "stats.nba.com",
    "User-Agent": random.choice(USER_AGENTS),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nba.com/game",
    "Origin": "https://www.nba.com",
    "Connection": "keep-alive",
    "Cookie": "your_real_browser_cookie_here"
}

def game_already_ingested(game_id: str) -> bool:
    query = text("""
        SELECT 1 FROM team_game_advanced
        WHERE game_id = :gid
        LIMIT 1;
    """)

    with engine.begin() as conn:
        result = conn.execute(query, {"gid": game_id}).fetchone()

    return result is not None

def fetch_team_stats(game_id: str):
    print(f"Warming session for game {game_id}...")

    # 🔥 handshake request (fast and reliable)
    boxscoretraditionalv3.BoxScoreTraditionalV3(game_id=game_id)

    time.sleep(1)

    print("Fetching advanced stats...")

    # now advanced works reliably
    boxscore = boxscoreadvancedv2.BoxScoreAdvancedV2(
        game_id=game_id,
        timeout=120
    )

    df = boxscore.get_data_frames()[1]
    team_df = df[df["PLAYER_ID"] == 0].copy()

    return team_df

def insert_team_stats(game_id: str, team_df):
    insert_query = text("""
        INSERT INTO team_game_advanced (
            game_id,
            team_id,
            team_name,
            offensive_rating,
            defensive_rating,
            pace,
            true_shooting_pct,
            effective_fg_pct,
            assist_pct,
            turnover_pct,
            rebound_pct
        )
        VALUES (
            :game_id,
            :team_id,
            :team_name,
            :off_rtg,
            :def_rtg,
            :pace,
            :ts,
            :efg,
            :ast,
            :tov,
            :reb
        )
    """)

    with engine.begin() as conn:
        for _, row in team_df.iterrows():
            conn.execute(insert_query, {
                "game_id": game_id,
                "team_id": int(row["TEAM_ID"]),
                "team_name": row["TEAM_NAME"],
                "off_rtg": float(row["OFF_RATING"]),
                "def_rtg": float(row["DEF_RATING"]),
                "pace": float(row["PACE"]),
                "ts": float(row["TS_PCT"]),
                "efg": float(row["EFG_PCT"]),
                "ast": float(row["AST_PCT"]),
                "tov": float(row["TOV_PCT"]),
                "reb": float(row["REB_PCT"])
            })

    print("Inserted team stats into DB.")

def ingest_game(game_id: str):
    if game_already_ingested(game_id):
        print("Game already injested. Skipping.")
        return
    
    team_df = fetch_team_stats(game_id)
    insert_team_stats(game_id, team_df)

if __name__ == "__main__":
    ingest_game("0022300061")
    time.sleep(1)
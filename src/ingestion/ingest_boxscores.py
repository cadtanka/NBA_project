# TO RUN: python ingest_boxscores.py

from sqlalchemy import create_engine, text
from nba_api.stats.endpoints import boxscoretraditionalv2, boxscoreadvancedv2
import time
import pandas as pd

engine = create_engine("postgresql://localhost/nba_tracking")

def get_pending_games():
    query = """
        SELECT game_id
        FROM ingestion_log
        WHERE boxscore_done = FALSE
        LIMIT 50
    """

    return pd.read_sql(query, engine)

def fetch_traditional(game_id):
    box = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
    df = box.get_data_frames()[0]
    return df

def fetch_advanced(game_id):
    adv = boxscoreadvancedv2.BoxScoreAdvancedV2(game_id=game_id)
    df = adv.get_data_frames()[0]
    return df

def transform_traditional(df):
    df = df.rename(columns={
        "GAME_ID": "game_id",
        "PLAYER_ID": "player_id",
        "TEAM_ID": "team_id",
        "MIN": "minutes",
        "PTS": "points",
        "REB": "rebounds",
        "AST": "assists",
        "STL": "steals",
        "BLK": "blocks",
        "TOV": "turnovers",
        "FGM": "fgm",
        "FGA": "fga",
        "FG3M": "fg3m",
        "FG3A": "fg3a",
        "FTM": "ftm",
        "FTA": "fta",
        "PLUS_MINUS": "plus_minus"
    })

    return df[[
        "game_id","player_id","team_id","minutes","points","rebounds",
        "assists","steals","blocks","turnovers","fgm","fga",
        "fg3m","fg3a","ftm","fta","plus_minus"
    ]]

def transform_advanced(df):
    df = df.rename(columns={
        "GAME_ID": "game_id",
        "PLAYER_ID": "player_id",
        "OFF_RATING": "offensive_rating",
        "DEF_RATING": "defensive_rating",
        "USG_PCT": "usage_pct",
        "TS_PCT": "true_shooting_pct",
        "PACE": "pace",
        "PIE": "pie"
    })

    return df[[
        "game_id",
        "player_id",
        "offensive_rating",
        "defensive_rating",
        "usage_pct",
        "true_shooting_pct",
        "pace",
        "pie"
    ]]

def mark_boxscore_done(game_id):
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE ingestion_log SET boxscore_done = TRUE WHERE game_id=:gid"),
            {"gid": game_id}
        )

def mark_advanced_done(game_id):
    with engine.begin() as conn:
        conn.execute(
            text("""
                UPDATE ingestion_log
                SET advanced_done = TRUE
                WHERE game_id=:gid
            """),
            {"gid": game_id}
        )

def get_pending_advanced_games():
    query = """
        SELECT game_id
        FROM ingestion_log
        WHERE advanced_done = FALSE
        LIMIT 50
    """

    return pd.read_sql(query, engine)

def ingest_advanced():
    games = get_pending_advanced_games()

    for game_id in games["game_id"]:
        try:
            print("Advanced stats:", game_id)

            df = fetch_advanced(game_id)
            df = transform_advanced(df)

            df.to_sql(
                "player_game_advanced",
                engine,
                if_exists="append",
                index=False
            )

            mark_advanced_done(game_id)

            time.sleep(0.7)

        except Exception as e:
            print("Advanced failed:", game_id, e)
            time.sleep(2)

def main():
    games = get_pending_games()

    for game_id in games["game_id"]:
        try:
            print("Processing", game_id)

            df = fetch_traditional(game_id)
            df = transform_traditional(df)

            df.to_sql("player_game_boxscore", engine, if_exists="append", index=False)

            mark_boxscore_done(game_id)

            time.sleep(0.7)
        
        except Exception as e:
            print("Failed:", game_id, e)
            time.sleep(2)

if __name__ == "__main__":
    print("Starting traditional boxscore ingestion")
    main()

    print("Starting advanced stats ingestion")
    ingest_advanced()
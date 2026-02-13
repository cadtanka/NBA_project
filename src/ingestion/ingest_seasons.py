from nba_api.stats.endpoints import leaguegamefinder
from sqlalchemy import create_engine
import pandas as pd
import time

engine = create_engine("postgresql://localhost/nba_tracking")

SEASONS = ["2023-2024", "2024-2025"]

def fetch_games_for_season(season):
    finder = leaguegamefinder.LeagueGameFinder(season_nullable=season)
    df = finder.get_data_frames()[0]

    games = df[[
        "GAME_ID",
        "GAME_DATE",
        "SEASON_ID",
        "TEAM_ID",
        "MATCHUP"
    ]].drop_duplicates(subset="GAME_TD")

    return games

def store_games(df):
    df.rename(columns={
        "GAME_ID": "game_id",
        "GAME_DATE": "game_date",
        "SEASON_ID": "season"
    }) [["game_id", "game_date", "season"]].to_sql(
        "games", engine, if_exists="append", index=False
    )

def populate_ingestion_log(df):
    ids = pd.DataFrame({"game_id": df["GAME_ID"].unique()})
    ids.to_sql("ingestion_log", engine, if_exists="append", index=False)

def main():
    for season in SEASONS:
        print("Fetching season", season)
        games = fetch_games_for_season(season)
        store_games(games)
        populate_ingestion_log(games)
        time.sleep(1)

if __name__ == "__main__":
    main()
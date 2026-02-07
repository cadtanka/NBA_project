from sqlalchemy import text
from db_entrypoint import engine

def create_tables():
    with engine.connection() as conn:
        conn.excute(text("""
            CREATE TABLES IF NOT EXISTS games (
            id SERIAL PRIMARY KEY,
            game_date DATE,
            home_team TEXT,
            away_team TEXT,
            video_path TEXT
        );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY
            game_date DATE,
            home_team TEXT,
            away_team_ TEXT,
            video_path TEXT
        );
        """))

        conn.execute(text("""
            CREATE TABLE players (
            id SERIAL PRIMARY KEY,
            jersey_number INT,
            team TEXT,
            jersey_color TEXT
        );
        """))

        conn.execute(text("""
            CREATE TABLE frames(
            id SERIAL PRIMARY KEY,
            game_id INT REFERENCES games(id)
            frame_number INT,
            game_clock FLOAT
        );
        """))

        conn.execute(text("""
            CREATE TABLE player_positions(
            id SERIAL PRIMARY KEY,
            frame_id INT REFERENCES frames(id),
            player_id INT REFERENCES players(id),

            x1 FLOAT,
            y1 FLOAT,
            x2 FLOAT,
            y2 FLOAT,
            cx FLOAT,
            cy FLOAT,
            zone TEXT,

            confidence FLOAT
        );
        """))

        conn.commit()


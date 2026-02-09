"""

*** TO CLEAR DATABASE TABLES ***
DROP TABLE IF EXISTS player_positions;
DROP TABLE IF EXISTS frames;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS games;

"""

from sqlalchemy import text
from src.data.db_entrypoint import engine
import pandas as pd

def create_tables():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS games (
            id SERIAL PRIMARY KEY,
            game_date DATE,
            home_team TEXT,
            away_team TEXT,
            video_path TEXT
            );
        """))

        conn.execute(text(""" 
            CREATE TABLE IF NOT EXISTS players ( 
            id SERIAL PRIMARY KEY, 
            assigned_number INT, 
            team TEXT, 
            jersey_color TEXT 
            );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS frames(
            id SERIAL PRIMARY KEY,
            game_id INT REFERENCES games(id),
            frame_number INT,
            game_clock FLOAT
            );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS player_positions(
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

def insert_game(game_date, home_team, away_team, video_path):
    with engine.begin() as conn:
        result = conn.execute(text("""
                INSERT INTO games (game_date, home_team, away_team, video_path)
                VALUES (:date, :home, :away, :path)
                RETURNING id; 
            """), {
                "date": game_date,
                "home": home_team,
                "away": away_team,
                "path": video_path
            })
        
        return result.scalar()
    
def get_or_create_player(assigned_number, team, jersey_color):
    with engine.begin() as conn:
        result = conn.execute(text("""
            SELECT id FROM players
            WHERE assigned_number=:num AND team=:team;
        """), {"num": assigned_number, "team": team})

        row = result.fetchone()

        if row:
            return row[0]
        
        result = conn.execute(text("""
            INSERT INTO players (assigned_number, team, jersey_color)
            VALUES (:num, :team, :color)
            RETURNING id;
        """), {
            "num": assigned_number,
            "team": team,
            "color": jersey_color
        })

        return result.scalar()

def insert_frame(game_id, frame_number, game_clock):
    with engine.begin() as conn:
        result = conn.execute(text("""
            INSERT INTO frames(game_id, frame_number, game_clock)
            VALUES (:gid, :frame, :clock)
            RETURNING id;
        """), {
            "gid": game_id,
            "frame": frame_number,
            "clock": game_clock
        })

        return result.scalar()
    
def insert_player_position(frame_id, player_id,
                            x1,y1,x2,y2,cx,cy,
                            zone, confidence):
    
    x1, y1, x2, y2 = map(float, (x1, y1, x2, y2)) 
    cx, cy = float(cx), float(cy) 
    confidence = float(confidence)

    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO player_positions
            (frame_id, player_id, x1, y1, x2, y2, cx, cy, zone, confidence)
            VALUES (:fid, :pid, :x1, :y1, :x2, :y2, :cx, :cy, :zone, :conf);
        """), {
            "fid": frame_id,
            "pid": player_id,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "cx": cx,
            "cy": cy,
            "zone": zone,
            "conf": confidence
        })


def get_tracking_dataframe(game_id: int):
    query = text("""
        SELECT
            f.frame_number AS frame,
            p.id AS track_id,
            p.team,
            pp.cx,
            pp.cy,
            pp.zone
        FROM player_positions pp
        JOIN frames f ON pp.frame_id = f.id
        JOIN players p ON pp.player_id = p.id
        WHERE f.game_id = :game_id
        ORDER BY f.frame_number;
    """)

    with engine.begin() as conn:
        df = pd.read_sql(query, conn, params={"game_id": game_id})

    return df
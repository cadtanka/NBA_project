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
from datetime import date

def get_games(game_id: int):
    query = text("""
        SELECT id, game_date, home_team, away_team, video_path
        FROM games
        WHERE id = :game_id
    """)

    with engine.begin() as conn:
        result = conn.execute(query, {"game_id": game_id}).mappings().first()

    if not result:
        return None
    
    result = dict(result)

    if isinstance(result["game_date"], date):
        result["game_date"] = result["game_date"].isoformat()

    # Transform DB row into API response shape
    return { 
            "game_id": result["id"], 
            "status": "completed", # or fetch from DB if you add this column later 
            "teams": [result["home_team"], result["away_team"]], 
            "date": result["game_date"], 
            }

def get_positions_in_timerange(game_id: int, start_time: float, end_time: float):
    query = text("""
        SELECT
            p.id as player_id,
            f.game_clock,
            pp.cx,
            pp.cy,
            pp.zone
        FROM player_posititions pp
        JOIN frame f ON pp.frame_id = f.id
        JOIN players p ON pp.player_id = p.id
        WHERE f.game_id = :game_id
        AND f.game_clock BETWEEN :start_time AND :end_time
        ORDER BY f.game_clock
    """)

    with engine.begin() as conn:
        rows = conn.execute(query, {
            "game_id": game_id,
            "start_time": start_time,
            "end_time": end_time
        }).mappings().all()

    return [dict(r) for r in rows]

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

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ingestion_log (
                game_id TEXT PRIMARY KEY,
                boxscore_done BOOLEAN DEFAULT FALSE<
                advanced_done BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

def get_full_tracking(game_id: int):
    query = text("""
        SELECT
            f.game_clock,
            p.id AS player_id,
            p.team,
            pp.cx,
            pp.cy
        FROM frames f
        JOIN player_positions pp ON pp.frame_id = f.id
        JOIN players p ON pp.player_id = p.id
        WHERE f.game_id = :game_id
        ORDER BY f.game_clock;
    """)

    with engine.begin() as conn:
        rows = conn.execute(query, {"game_id": game_id}).mappings().all()

    return [dict(r) for r in rows]
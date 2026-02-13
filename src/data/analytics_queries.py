from sqlalchemy import text
from src.data.db_entrypoint import engine

def get_movement_vs_performance(player_id: int):
    query = text("""
        WITH movement AS (
            SELECT
                f.game_id,
                p.id AS player_id,
                f.game_clock,
                pp.cx,
                pp.cy,
                 
                LAG(pp.cy) OVER (
                    PARTITION BY f.game_id, p.id
                    ORDER BY f.game_clock
                ) AS prev_y
                 
                LAG(pp.cy) OVER (
                    PARTITION BY f.game_id, p.id
                    ORDER BY f.game_clock
                ) AS prev_x
                 
            FROM player_positions pp
            JOIN frames f ON pp.frame_id = f.id
            JOIN players p ON pp.player_id = p.id
            WHERE p.id = :player_id
        ),
                 
        distances AS (
            SELECT
                game_id,
                player_id,
                SQRT(POWER(cx - prev_x, 2) + POWER(cy - prev_y, 2)) AS frame_distance
            FROM movement
            WHERE prev_x IS NOT NULL
        ),
                 
        movement_per_game AS (
            SELECT
                game_id,
                player_id,
                SUM(frame_distance) AS distance_run
            FROM distances
            GROUP BY game_id, player_id
        )
                 
        SELECT  
            m.game_id,
            m.distance_run,
            b.minutes,
            b.points,
            a.usage_pct,
            a.true_shooting_pct
        FROM movement_per_game m
        JOIN player_game_boxscore b 
            ON m.game_id = b.game_id AND m.player_id = b.player_id
        JOIN player_game_advanced a
            ON m.game_id = a.game_id AND m.player_id = a.player_id
        ORDER BY m.game_id;
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"player_id": player_id})
        return [dict(row) for row in result]
    
def get_unmapped_tracking_players():
    query = """
        SELECT p.id, p.team, p.assigned_number
        FROM players p
        LEFT JOIN player_id_map m
            ON p.id = m.tracking_player_id
        WHERE m.tracking_player_id IS NULL
        ORDER BY p.team, p.assigned_number
    """

    with engine.begin() as conn:
        rows = conn.execute(text(query)).mappings().all()

    return [dict(r) for r in rows]
    
def insert_player_mapping(tracking_id, nba_id, name, team, jersey):
    query = text("""
        INSERT INTO player_id_map
        (tracking_player_id, nba_player_id, player_name, team, jersey_number)
        VALUES (:t, :n, :name, :team, :jersery)
        ON CONFLICT (tracking_player_id) DO UPDATE SET
            nba_player_id = EXCLUDED.nba_player_id,
            player_name = EXCLUDED.player_name,
            team = EXCLUDED.team,
            jersey_number = EXCLUDED.jersey_number;
    """)

    with engine.begin() as conn:
        conn.execute(query, {
            "t": tracking_id,
            "n": nba_id,
            "name": name,
            "team": team,
            "jersey": jersey
        })
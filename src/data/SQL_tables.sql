CREATE TABLES games (
    id SERIAL PRIMARY KEY,
    game_date DATE,
    home_team TEXT,
    away_team TEXT,
    video_path TEXT
)

CREATE TABLE players (
    id SERIAL PRIMARY KEY
    game_date DATE,
    home_team TEXT,
    away_team_ TEXT,
    video_path TEXT
)

CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    jersey_number INT,
    team TEXT,
    jersey_color TEXT
);

CREATE TABLE frames(
    id SERIAL PRIMARY KEY,
    game_id INT REFERENCES games(id)
    frame_number INT,
    game_clock FLOAT
);

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

CREATE INDEX idx_frames_game_clock
ON frames(game_id, game_clock)

CREATE INDEX idx_player_positions_frame
ON player_positions(frame_id)

CREATE INDEX idx_player_positions_player
ON player_positions(player_id)
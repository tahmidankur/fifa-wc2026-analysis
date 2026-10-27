-- World Cup 2026 database schema (SQLite)
--
--   teams    one row per team (48)
--   players  one row per player who played, linked to their team
--   matches  one row per match (104), linked to two teams
--
-- Oracle note: use NUMBER instead of INTEGER and VARCHAR2 instead of TEXT.

DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS teams;

CREATE TABLE teams (
    team_id        INTEGER PRIMARY KEY,
    team_name      TEXT    NOT NULL UNIQUE,
    fifa_code      TEXT    NOT NULL UNIQUE,
    group_name     TEXT    NOT NULL,
    confederation  TEXT    NOT NULL
);

CREATE TABLE players (
    player_id     INTEGER PRIMARY KEY,
    player_name   TEXT    NOT NULL,
    team_id       INTEGER NOT NULL,
    position      TEXT    NOT NULL CHECK (position IN ('GK', 'DF', 'MF', 'FW')),
    matches       INTEGER NOT NULL CHECK (matches BETWEEN 1 AND 8),
    minutes       INTEGER NOT NULL CHECK (minutes > 0),
    goals         INTEGER NOT NULL CHECK (goals >= 0),
    assists       INTEGER NOT NULL CHECK (assists >= 0),
    yellow_cards  INTEGER NOT NULL DEFAULT 0,
    red_cards     INTEGER NOT NULL DEFAULT 0,
    -- no goals_per_90 column: it can be worked out from goals and minutes
    FOREIGN KEY (team_id) REFERENCES teams (team_id)
);

-- Each match points at the teams table twice, once for each side.
CREATE TABLE matches (
    match_id      INTEGER PRIMARY KEY,
    match_date    TEXT    NOT NULL,
    stage         TEXT    NOT NULL,
    home_team_id  INTEGER NOT NULL,
    away_team_id  INTEGER NOT NULL,
    home_goals    INTEGER NOT NULL CHECK (home_goals >= 0),
    away_goals    INTEGER NOT NULL CHECK (away_goals >= 0),
    result_type   TEXT    NOT NULL CHECK (result_type IN ('Regular', 'AET', 'Penalties')),
    CHECK (home_team_id <> away_team_id),
    FOREIGN KEY (home_team_id) REFERENCES teams (team_id),
    FOREIGN KEY (away_team_id) REFERENCES teams (team_id)
);

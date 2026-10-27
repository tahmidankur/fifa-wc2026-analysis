# Step 2: build database/worldcup.db from sql/schema.sql and the cleaned CSVs
#
# Run from the project folder (after step 1):
#     python scripts/02_build_database.py

import os
import sqlite3
import pandas as pd

os.makedirs("database", exist_ok=True)
DB_PATH = "database/worldcup.db"

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")   # SQLite has them off by default

with open("sql/schema.sql") as f:
    conn.executescript(f.read())

teams = pd.read_csv("data/cleaned/teams_clean.csv")
players = pd.read_csv("data/cleaned/players_clean.csv")
matches = pd.read_csv("data/cleaned/matches_clean.csv")

# The CSVs have some calculated columns (goals_per_90, goals_for...) that
# the database doesn't store, so only the table columns get inserted.
team_columns = ["team_id", "team_name", "fifa_code", "group_name", "confederation"]
player_columns = ["player_id", "player_name", "team_id", "position", "matches",
                  "minutes", "goals", "assists", "yellow_cards", "red_cards"]

# Teams first, because players and matches both point to them.
teams[team_columns].to_sql("teams", conn, if_exists="append", index=False)
players[player_columns].to_sql("players", conn, if_exists="append", index=False)
matches.to_sql("matches", conn, if_exists="append", index=False)
conn.commit()

for table in ["teams", "players", "matches"]:
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table:<8} {count} rows")

problems = conn.execute("PRAGMA foreign_key_check").fetchall()
print("Foreign key problems:", len(problems))

conn.close()
print("Saved", DB_PATH)

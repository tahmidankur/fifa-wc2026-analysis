# Step 4: copy the charts and player data into docs/ for the GitHub Pages site
#
# Run from the project folder (after steps 1 and 3):
#     python scripts/04_build_site.py

import os
import shutil
import pandas as pd

os.makedirs("docs/charts", exist_ok=True)

for name in os.listdir("charts"):
    if name.endswith(".png"):
        shutil.copy(f"charts/{name}", f"docs/charts/{name}")

players = pd.read_csv("data/cleaned/players_clean.csv")
teams = pd.read_csv("data/cleaned/teams_clean.csv")
players = players.merge(teams[["team_id", "team_name"]], on="team_id")

columns = ["player_name", "team_name", "position", "matches", "minutes",
           "goals", "assists", "goals_per_90"]
players = players[columns].sort_values(["goals", "assists"], ascending=False)
players.to_json("docs/players.json", orient="values", force_ascii=False)

print("Copied charts and wrote docs/players.json with", len(players), "players")

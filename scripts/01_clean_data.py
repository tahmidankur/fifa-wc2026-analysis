# Step 1: clean the raw CSV files and save them to data/cleaned/
#
# Run from the project folder:
#     python scripts/01_clean_data.py

import os
import re
import pandas as pd

os.makedirs("data/cleaned", exist_ok=True)

MIN_MINUTES = 180   # below this, per-90 numbers are mostly noise

players = pd.read_csv("data/raw/player_stats.csv")
teams = pd.read_csv("data/raw/teams.csv")
matches = pd.read_csv("data/raw/matches.csv")
stages = {1: "Group Stage", 2: "Round of 32", 3: "Round of 16", 4: "Quarter-final",
          5: "Semi-final", 6: "Third place", 7: "Final"}

print("players:", len(players), " teams:", len(teams), " matches:", len(matches))


# 1. Squad players who never played
# Every team named 26 players, but some never got on the pitch.
unused = players["minutes_played"] == 0
print("Removed", unused.sum(), "squad players with 0 minutes")
players = players[~unused].copy()


# 2. Broken player names
# Some names came through scrambled, e.g. "MARTINELLIGabriel Gabriel" or
# "Matheus Matheus Cunha". Two rules fix most of them:
#   - surname in capitals stuck to the first name -> "Gabriel Martinelli"
#   - the same word twice in a row -> keep one
def fix_name(name):
    caps = re.match(r"^([A-ZÀ-Þ]{2,})([A-Z][a-zà-ÿ]+)", name)
    if caps:
        name = caps.group(2) + " " + caps.group(1).title()
    words = name.split()
    words = [w for i, w in enumerate(words) if i == 0 or w != words[i - 1]]
    return " ".join(words)

before = players["player_name"].copy()
players["player_name"] = players["player_name"].map(fix_name)
print("Names fixed by the two rules:", (before != players["player_name"]).sum())

# The rest I fixed by hand (and shortened some long legal names, so
# "Lionel Andrés Messi" shows up as "Lionel Messi" in the charts).
name_fixes = pd.read_csv("data/raw/name_fixes.csv")
players = players.set_index("player_id")
players.loc[name_fixes["player_id"], "player_name"] = name_fixes["player_name"].values
print("Names fixed by hand:", len(name_fixes))


# 3. Wrong goal counts
# I checked every scorer against Wikipedia's list (which cites FIFA).
# Team totals matched, but 6 goals were credited to the wrong teammate,
# e.g. Barcola had 4 and Dembélé 5, when it should be 3 and 6.
goal_fixes = pd.read_csv("data/raw/goal_fixes.csv")
players.loc[goal_fixes["player_id"], "goals"] = goal_fixes["goals"].values
players = players.reset_index()
print("Goal counts corrected:", len(goal_fixes))


# 4. Position labels: DEF/MID/FWD -> DF/MF/FW
players["position"] = players["position"].replace({"DEF": "DF", "MID": "MF", "FWD": "FW"})
print("Positions:", sorted(players["position"].unique()))

# shots and xG are empty for every player in this source, so they're dropped
players = players[["player_id", "player_name", "team_id", "position", "matches_played",
                   "minutes_played", "goals", "assists", "yellow_cards", "red_cards"]]
players = players.rename(columns={"matches_played": "matches", "minutes_played": "minutes"})


# Matches: stage names instead of numbers, only the columns I use
matches["stage"] = matches["stage_id"].map(stages)
matches = matches.rename(columns={"date": "match_date", "home_score": "home_goals",
                                  "away_score": "away_goals"})
matches = matches[["match_id", "match_date", "stage", "home_team_id", "away_team_id",
                   "home_goals", "away_goals", "result_type"]]

# 5. A knockout match can't end in a draw, so a drawn one marked "Regular"
# must have gone to penalties (Switzerland 0-0 Colombia, won 4-3 on pens).
drawn_ko = ((matches["stage"] != "Group Stage")
            & (matches["home_goals"] == matches["away_goals"])
            & (matches["result_type"] == "Regular"))
matches.loc[drawn_ko, "result_type"] = "Penalties"
print("Drawn knockout matches fixed to Penalties:", drawn_ko.sum())

teams = teams.rename(columns={"group_letter": "group_name"})
teams = teams[["team_id", "team_name", "fifa_code", "group_name", "confederation"]]


# Calculated columns (only in the CSVs, not in the database)
players["goals_per_90"] = (players["goals"] / players["minutes"] * 90).round(2)

# Team totals, from both the home and away side of each match
home = matches.rename(columns={"home_team_id": "team_id", "home_goals": "gf", "away_goals": "ga"})
away = matches.rename(columns={"away_team_id": "team_id", "away_goals": "gf", "home_goals": "ga"})
both = pd.concat([home, away])
both["stage_no"] = both["stage"].map({v: k for k, v in stages.items()})

totals = both.groupby("team_id").agg(matches_played=("match_id", "count"),
                                     goals_for=("gf", "sum"),
                                     goals_against=("ga", "sum"),
                                     last_stage=("stage_no", "max"))
teams = teams.merge(totals, on="team_id")
teams["stage_reached"] = teams["last_stage"].map(stages)
# the third place match isn't a round further than the semis
teams["stage_reached"] = teams["stage_reached"].replace("Third place", "Semi-final")

final = matches[matches["stage"] == "Final"].iloc[0]
winner = final["home_team_id"] if final["home_goals"] > final["away_goals"] else final["away_team_id"]
teams.loc[teams["team_id"] == winner, "stage_reached"] = "Champion"
teams = teams.drop(columns="last_stage")
teams["goals_per_match"] = (teams["goals_for"] / teams["matches_played"]).round(2)


# Quick checks: goals in the player file should equal goals in the match
# scores, minus own goals (which aren't credited to anyone on the team).
own_goals = pd.read_csv("data/raw/player_stats.csv")["own_goals"].sum()
match_goals = matches["home_goals"].sum() + matches["away_goals"].sum()
print(f"Goals: {match_goals} in matches, {players['goals'].sum()} by players, {own_goals} own goals")
assert players["goals"].sum() + own_goals == match_goals
assert players["player_id"].is_unique

players_180 = players[players["minutes"] >= MIN_MINUTES]
print(f"Players with {MIN_MINUTES}+ minutes: {len(players_180)} of {len(players)}")

players.to_csv("data/cleaned/players_clean.csv", index=False)
players_180.to_csv("data/cleaned/players_180_minutes.csv", index=False)
teams.to_csv("data/cleaned/teams_clean.csv", index=False)
matches.to_csv("data/cleaned/matches_clean.csv", index=False)
print("Saved 4 files to data/cleaned/")

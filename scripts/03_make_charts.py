# Step 3: make the charts in charts/
#
# Run from the project folder (after step 1):
#     python scripts/03_make_charts.py

import os
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs("charts", exist_ok=True)

players = pd.read_csv("data/cleaned/players_180_minutes.csv")
all_players = pd.read_csv("data/cleaned/players_clean.csv")
teams = pd.read_csv("data/cleaned/teams_clean.csv")
matches = pd.read_csv("data/cleaned/matches_clean.csv")

players = players.merge(teams[["team_id", "team_name"]], on="team_id")
all_players = all_players.merge(teams[["team_id", "team_name"]], on="team_id")

plt.rcParams["figure.dpi"] = 150
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False
plt.rcParams["font.size"] = 10

BLUE = "#1f6fae"
RED = "#c8553d"
GREY = "#b4bcc5"


# Chart 1: top 10 scorers
top = all_players.sort_values(["goals", "assists"], ascending=False).head(10).iloc[::-1]
labels = top["player_name"] + " (" + top["team_name"] + ")"

fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(labels, top["goals"], color=BLUE, height=0.6)
for i, goals in enumerate(top["goals"]):
    ax.text(goals + 0.1, i, str(goals), va="center")
ax.set_xlabel("Goals")
ax.set_title("Top 10 scorers, World Cup 2026")
plt.tight_layout()
plt.savefig("charts/01_top_scorers.png")
plt.close()


# Chart 2: goals per 90, minimum 180 minutes
best = players.sort_values("goals_per_90", ascending=False).head(10).iloc[::-1]
labels = best["player_name"] + " (" + best["minutes"].astype(str) + " min)"

fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(labels, best["goals_per_90"], color=BLUE, height=0.6)
for i, value in enumerate(best["goals_per_90"]):
    ax.text(value + 0.02, i, f"{value:.2f}", va="center")
ax.set_xlabel("Goals per 90 minutes")
ax.set_title("Goals per 90 (180+ minutes played)")
plt.tight_layout()
plt.savefig("charts/02_goals_per_90.png")
plt.close()


# Chart 3: goals per match in each round
rounds = ["Group Stage", "Round of 32", "Round of 16", "Quarter-final", "Semi-final", "Final"]
matches["total_goals"] = matches["home_goals"] + matches["away_goals"]
by_round = matches[matches["stage"].isin(rounds)].groupby("stage")["total_goals"].agg(["mean", "count"])
by_round = by_round.reindex(rounds)

labels = [f"{stage}\n({n} match{'es' if n > 1 else ''})" for stage, n in zip(rounds, by_round["count"])]

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar(labels, by_round["mean"], color=BLUE, width=0.6)
for i, avg in enumerate(by_round["mean"]):
    ax.text(i, avg + 0.05, f"{avg:.2f}", ha="center")
ax.set_ylabel("Goals per match")
ax.set_title("Goals per match by round (third place match left out)")
ax.set_ylim(0, 3.5)
plt.tight_layout()
plt.savefig("charts/03_goals_by_round.png")
plt.close()


# Chart 4: scored vs conceded per match, every team
teams["conceded_per_match"] = teams["goals_against"] / teams["matches_played"]
semis = teams["stage_reached"].isin(["Semi-final", "Final", "Champion"])

fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(teams.loc[~semis, "conceded_per_match"], teams.loc[~semis, "goals_per_match"],
           color=GREY, s=40, label="Other teams")
ax.scatter(teams.loc[semis, "conceded_per_match"], teams.loc[semis, "goals_per_match"],
           color=RED, s=60, label="Semi-finalists")

for _, row in teams[semis].iterrows():
    ax.annotate(row["team_name"], (row["conceded_per_match"], row["goals_per_match"]),
                xytext=(6, 3), textcoords="offset points", fontsize=8)

ax.set_xlabel("Goals conceded per match")
ax.set_ylabel("Goals scored per match")
ax.set_title("Goals scored vs conceded per match, all 48 teams")
ax.legend(loc="upper right", frameon=False)
plt.tight_layout()
plt.savefig("charts/04_scored_vs_conceded.png")
plt.close()

print("Saved 4 charts to charts/")

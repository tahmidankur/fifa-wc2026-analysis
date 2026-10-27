# Data dictionary

## teams (48 rows)

| Column | Type | Meaning |
| --- | --- | --- |
| `team_id` | integer | Primary key |
| `team_name` | text | Country |
| `fifa_code` | text | Three-letter code, e.g. ESP |
| `group_name` | text | Group A to L |
| `confederation` | text | UEFA, CONMEBOL, CAF, AFC, CONCACAF, OFC |

Extra columns in `teams_clean.csv` only (worked out from the matches):
`matches_played`, `goals_for`, `goals_against`, `goals_per_match`, and
`stage_reached` (Group Stage, Round of 32, Round of 16, Quarter-final,
Semi-final, Final, Champion).

## players (1,039 rows)

Only players who got on the pitch.

| Column | Type | Meaning |
| --- | --- | --- |
| `player_id` | integer | Primary key |
| `player_name` | text | |
| `team_id` | integer | Foreign key to `teams` |
| `position` | text | GK, DF, MF or FW |
| `matches` | integer | Matches played in |
| `minutes` | integer | Total minutes |
| `goals` | integer | Checked against Wikipedia |
| `assists` | integer | From the source, not checked |
| `yellow_cards` | integer | |
| `red_cards` | integer | |

Extra column in the CSVs: `goals_per_90` = `goals / minutes * 90`.

`players_180_minutes.csv` is the same list cut down to players with 180+
minutes (two full matches). The per-90 chart and the dashboard use it.

## matches (104 rows)

| Column | Type | Meaning |
| --- | --- | --- |
| `match_id` | integer | Primary key |
| `match_date` | text | YYYY-MM-DD |
| `stage` | text | Group Stage, Round of 32, Round of 16, Quarter-final, Semi-final, Third place, Final |
| `home_team_id` | integer | Foreign key to `teams` |
| `away_team_id` | integer | Foreign key to `teams` |
| `home_goals` | integer | Goals after 90 or 120 minutes, not counting a shootout |
| `away_goals` | integer | Same |
| `result_type` | text | Regular, AET (extra time) or Penalties |

## Fix files (in data/raw/)

- `name_fixes.csv`: player_id and the corrected name
- `goal_fixes.csv`: player_id and the correct goal count

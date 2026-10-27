# Power BI dashboard

Power BI Desktop only runs on Windows. On a Mac, use a Windows computer (a
uni lab machine works) and copy the `data/cleaned/` folder over.

## 1. Load the data

Home > Get Data > Text/CSV, and load:

- `players_180_minutes.csv`, renamed to **Players**
- `teams_clean.csv`, renamed to **Teams**
- `matches_clean.csv`, renamed to **Matches**

In Transform Data, check that `goals_per_90` and `goals_per_match` are
decimal numbers, not whole numbers.

## 2. Relationship

In Model view, make sure `Players[team_id]` is linked to `Teams[team_id]`
(many to one). Drag one onto the other if it isn't.

Leave Matches unlinked. It points to Teams twice (home and away) and Power BI
only allows one active link, which makes it confusing. It's only used for the
round chart.

## 3. Measures

On the Players table, New Measure:

```
Total Goals = SUM(Players[goals])

Goals per 90 = DIVIDE(SUM(Players[goals]) * 90, SUM(Players[minutes]))

Players Counted = COUNTROWS(Players)
```

On the Matches table:

```
Goals per Match = AVERAGEX(Matches, Matches[home_goals] + Matches[away_goals])
```

## 4. Page layout

Top row, three **Cards**: Total Goals, Goals per 90 (2 decimals), Players Counted.

Middle left, **clustered bar chart**: `player_name` and `goals`. In the
Filters pane, set `player_name` to Top N = 10 by `goals`.

Middle right, **column chart**: `Matches[stage]` and `Goals per Match`.
Sort the axis by round, not alphabetically (or filter out Third place).

Bottom, **table**: `player_name`, `team_name`, `position`, `minutes`,
`goals`, `assists`, `goals_per_90`.

Slicers on the right: `Teams[team_name]` (dropdown) and `Players[position]`.

Pick a team in the slicer and the cards, bar chart and table should change.
The round chart won't, because Matches isn't linked.

## 5. Finish

- Give every visual a short title.
- Check the cards don't show long decimals.
- Save, screenshot the page as `charts/dashboard.png`, and un-comment the
  dashboard line in the README.

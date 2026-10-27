-- World Cup 2026 queries
--
-- Run in DB Browser for SQLite (Execute SQL tab), or:
--     sqlite3 -header -column database/worldcup.db < sql/queries.sql
--
-- "* 1.0" or "90.0" shows up a lot below. SQLite does whole-number division
-- when both sides are integers (5 / 2 = 2), so this forces a decimal.
-- Oracle: use FETCH FIRST 10 ROWS ONLY instead of LIMIT 10.


-- 1. Top 10 scorers
SELECT p.player_name, t.team_name, p.goals, p.assists, p.minutes
FROM players p
JOIN teams t ON p.team_id = t.team_id
ORDER BY p.goals DESC, p.assists DESC
LIMIT 10;


-- 2. Goals per 90 minutes, players with 180+ minutes
-- Remove the minutes filter and players with one goal in 20 minutes
-- go straight to the top.
SELECT p.player_name, t.team_name, p.goals, p.minutes,
       ROUND(p.goals * 90.0 / p.minutes, 2) AS goals_per_90
FROM players p
JOIN teams t ON p.team_id = t.team_id
WHERE p.minutes >= 180
ORDER BY goals_per_90 DESC
LIMIT 10;


-- 3. Spain's scorers
SELECT p.player_name, p.position, p.goals
FROM players p
JOIN teams t ON p.team_id = t.team_id
WHERE t.team_name = 'Spain' AND p.goals > 0
ORDER BY p.goals DESC;


-- 4. Goals per 90 by position
-- Total goals / total minutes, so a player with 600 minutes counts more
-- than one with 30.
SELECT position,
       COUNT(*) AS players,
       SUM(goals) AS goals,
       ROUND(SUM(goals) * 90.0 / SUM(minutes), 3) AS goals_per_90
FROM players
GROUP BY position
ORDER BY goals_per_90 DESC;


-- 5. Every match with both team names
-- matches links to teams twice, so teams is joined twice with two aliases.
SELECT m.match_date, m.stage,
       h.team_name AS home, m.home_goals, m.away_goals, a.team_name AS away,
       m.result_type
FROM matches m
JOIN teams h ON m.home_team_id = h.team_id
JOIN teams a ON m.away_team_id = a.team_id
ORDER BY m.match_id;


-- 6. Goals per match in each round
SELECT stage,
       COUNT(*) AS matches,
       SUM(home_goals + away_goals) AS goals,
       ROUND(AVG(home_goals + away_goals), 2) AS goals_per_match
FROM matches
GROUP BY stage
ORDER BY MIN(match_id);


-- 7. Goals scored and conceded by each team
-- A team can be home or away, so the two sides are stacked with UNION ALL
-- first and then added up.
SELECT t.team_name,
       COUNT(*) AS played,
       SUM(s.scored) AS scored,
       SUM(s.conceded) AS conceded,
       SUM(s.scored) - SUM(s.conceded) AS goal_difference
FROM (
    SELECT home_team_id AS team_id, home_goals AS scored, away_goals AS conceded FROM matches
    UNION ALL
    SELECT away_team_id, away_goals, home_goals FROM matches
) s
JOIN teams t ON s.team_id = t.team_id
GROUP BY t.team_name
ORDER BY scored DESC
LIMIT 10;


-- 8. Knockout matches that needed extra time or penalties
SELECT m.stage, h.team_name AS home, m.home_goals, m.away_goals,
       a.team_name AS away, m.result_type
FROM matches m
JOIN teams h ON m.home_team_id = h.team_id
JOIN teams a ON m.away_team_id = a.team_id
WHERE m.result_type <> 'Regular'
ORDER BY m.match_id;


-- 9. Teams with at least 5 different scorers
-- HAVING filters after GROUP BY. WHERE can't, because the count
-- doesn't exist until the rows are grouped.
SELECT t.team_name, COUNT(*) AS scorers, SUM(p.goals) AS goals
FROM players p
JOIN teams t ON p.team_id = t.team_id
WHERE p.goals > 0
GROUP BY t.team_name
HAVING COUNT(*) >= 5
ORDER BY scorers DESC;


-- 10. Goals by confederation
SELECT t.confederation,
       COUNT(DISTINCT t.team_id) AS teams,
       SUM(p.goals) AS goals,
       ROUND(SUM(p.goals) * 1.0 / COUNT(DISTINCT t.team_id), 1) AS goals_per_team
FROM teams t
JOIN players p ON p.team_id = t.team_id
GROUP BY t.confederation
ORDER BY goals_per_team DESC;

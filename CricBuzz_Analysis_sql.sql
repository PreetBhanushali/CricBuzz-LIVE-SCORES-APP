-- Indian Players Details 
SELECT 
	name,
	role,
	battingStyle,
	bowlingStyle
FROM cricket_player_data
WHERE team_name = 'India';


-- top 10 highest run scorers in ODI cricket
SELECT
  player_name,
  runs AS total_runs,
  average AS batting_average,
  hundreds AS number_of_centuries
FROM (
  SELECT
    player_name,
    format,
    runs,
    average,
    hundreds
  FROM all_batsmen_stats
  UNION ALL
  SELECT
    player_name,
    format,
    runs,
    avg AS average,
    hundreds
  FROM all_rounders_batting_stats
) AS combined_stats
WHERE format = 'ODI'
ORDER BY runs DESC
LIMIT 10;


-- cricket venues with seating capacity more than 50,000 spectators.
SELECT
  ground AS venue_name,
  city,
  country,
  capacity
FROM venue_info
WHERE capacity > 50000
ORDER BY capacity DESC;

--Players Role Distribution

SELECT
  role,
  COUNT(id) AS player_count
FROM cricket_player_data
GROUP BY role;


--  highest individual batting score achieved in each cricket format.
SELECT
  format,
  MAX(highest_score) AS highest_score
FROM (
  SELECT
    format,
    highest_score
  FROM all_batsmen_stats
  UNION ALL
  SELECT
    format,
    high_score AS highest_score
  FROM all_rounders_batting_stats
) AS combined_stats
WHERE format IN ('Test', 'ODI', 'T20','IPL')
GROUP BY format;


-- cricket series that started in the year 2024.
SELECT
  name AS series_name,
  series_type AS match_type,
  start_date
FROM all_cricket_series
WHERE STRFTIME('%Y', start_date) = '2024';


-- Really Good All-Rounders Details
SELECT
  b.player_name,
  b.runs AS total_runs,
  w.wickets AS total_wickets,
  b.format
FROM "all_rounders_batting_stats" b
JOIN "all_rounders_bowling_stats" w
  ON b.player_id = w.player_id AND b.format = w.format
WHERE
  b.runs > 1000 AND w.wickets > 50;

  
-- each player's performance across different cricket formats.
SELECT
  player_name,
  SUM(CASE WHEN format = 'Test' THEN runs ELSE 0 END) AS Test_Runs,
  SUM(CASE WHEN format = 'ODI' THEN runs ELSE 0 END) AS ODI_Runs,
  SUM(CASE WHEN format = 'T20' THEN runs ELSE 0 END) AS T20_Runs
FROM (
  SELECT
    player_name,
    format,
    runs
  FROM all_batsmen_stats
  UNION ALL
  SELECT
    player_name,
    format,
    runs
  FROM all_rounders_batting_stats
) AS combined_stats
WHERE
  player_name IN (
    SELECT player_name
    FROM (
      SELECT player_name, format FROM all_batsmen_stats
      UNION ALL
      SELECT player_name, format FROM all_rounders_batting_stats
    ) AS all_formats
    GROUP BY player_name
    HAVING COUNT(DISTINCT format) >= 2
  )
GROUP BY
  player_name
ORDER BY
  player_name,Test_Runs DESC;
  
 
--  most economical bowlers in limited-overs cricket 
SELECT
  player_name,
  ROUND(SUM(runs) * 6.0 / SUM(balls),2) AS overall_economy_rate,
  SUM(wickets) AS total_wickets
FROM (
  SELECT player_name, format, matches, balls, runs, wickets FROM all_bowlers_stats
  UNION ALL
  SELECT player_name, format, matches, balls, runs, wickets FROM all_rounders_bowling_stats
) AS combined_bowling_stats
WHERE
  format IN ('ODI', 'T20') AND matches >= 10 AND balls / matches >= 12
GROUP BY
  player_name
ORDER BY
  overall_economy_rate;
  
  
-- Player Match Counts and Batting Averages Across Formats (Min. 20 Matches)
WITH format_summary AS (
    SELECT 
        player_name,
        format,
        SUM(matches) AS matches,
        AVG(average) AS batting_avg
    FROM Overall_batsman_stats
    WHERE format IN ('Test', 'ODI', 'T20')
    GROUP BY player_name, format
),
pivoted AS (
    SELECT
        player_name,
        MAX(CASE WHEN format = 'Test' THEN matches END) AS matches_Test,
        MAX(CASE WHEN format = 'ODI' THEN matches END) AS matches_ODI,
        MAX(CASE WHEN format = 'T20' THEN matches END) AS matches_T20,
        MAX(CASE WHEN format = 'Test' THEN batting_avg END) AS avg_Test,
        MAX(CASE WHEN format = 'ODI' THEN batting_avg END) AS avg_ODI,
        MAX(CASE WHEN format = 'T20' THEN batting_avg END) AS avg_T20
    FROM format_summary
    GROUP BY player_name
)
SELECT *,
       COALESCE(matches_Test,0) + COALESCE(matches_ODI,0) + COALESCE(matches_T20,0) AS total_matches
FROM pivoted
WHERE (COALESCE(matches_Test,0) + COALESCE(matches_ODI,0) + COALESCE(matches_T20,0)) >= 20
ORDER BY total_matches DESC;


-- comprehensive performance ranking system for players.
WITH batting AS (
    SELECT 
        player_id,
        player_name,
        SUM(runs) AS total_runs,
        AVG(avg) AS batting_avg,
        AVG(strike_rate) AS strike_rate,
        (SUM(runs) * 0.01) 
        + (AVG(avg) * 0.5) 
        + (AVG(strike_rate) * 0.3) AS batting_points
    FROM all_rounders_batting_stats
    GROUP BY player_id, player_name
),
bowling AS (
    SELECT
        player_id,
        player_name,
        SUM(wickets) AS total_wickets,
        AVG(avg) AS bowling_avg,
        AVG(eco) AS economy,
        (SUM(wickets) * 2)
        + ((50 - AVG(avg)) * 0.5)
        + ((6 - AVG(eco)) * 2) AS bowling_points
    FROM all_rounders_bowling_stats
    GROUP BY player_id, player_name
),
-- LEFT JOIN (all batting, with bowling if available)
bat_left AS (
    SELECT
        b.player_id,
        b.player_name,
        b.total_runs,
        b.batting_avg,
        b.strike_rate,
        bo.total_wickets,
        bo.bowling_avg,
        bo.economy,
        b.batting_points,
        COALESCE(bo.bowling_points, 0) AS bowling_points
    FROM batting b
    LEFT JOIN bowling bo
        ON b.player_id = bo.player_id
),
-- RIGHT JOIN simulated (all bowling, with batting if available)
bowl_left AS (
    SELECT
        bo.player_id,
        bo.player_name,
        b.total_runs,
        b.batting_avg,
        b.strike_rate,
        bo.total_wickets,
        bo.bowling_avg,
        bo.economy,
        COALESCE(b.batting_points, 0) AS batting_points,
        bo.bowling_points
    FROM bowling bo
    LEFT JOIN batting b
        ON b.player_id = bo.player_id
)
-- UNION to simulate FULL OUTER JOIN
SELECT *,
       (batting_points + bowling_points) AS total_points
FROM bat_left
UNION
SELECT *,
       (batting_points + bowling_points) AS total_points
FROM bowl_left
ORDER BY total_points DESC;


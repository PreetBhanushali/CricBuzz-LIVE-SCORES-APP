import streamlit as st
import sqlite3
import pandas as pd

def app():
    # ==========================
    # Database configuration
    # ==========================
    DB_PATH = "CricBuzz_database.db"

    # ==========================
    # Queries dictionary
    # ==========================
    QUERIES = {
        "Indian Players Details": """
            SELECT name, role, battingStyle, bowlingStyle
            FROM cricket_player_data
            WHERE team_name = 'India';
        """,

        "Top 10 Highest Run Scorers in ODI": """
            SELECT player_name, runs AS total_runs, average AS batting_average, hundreds AS number_of_centuries
            FROM (
                SELECT player_name, format, runs, average, hundreds FROM all_batsmen_stats
                UNION ALL
                SELECT player_name, format, runs, avg AS average, hundreds FROM all_rounders_batting_stats
            ) AS combined_stats
            WHERE format = 'ODI'
            ORDER BY runs DESC
            LIMIT 10;
        """,

        "Venues with Capacity > 50,000": """
            SELECT ground AS venue_name, city, country, capacity
            FROM venue_info
            WHERE capacity > 50000
            ORDER BY capacity DESC;
        """,

        "Players Role Distribution": """
            SELECT role, COUNT(id) AS player_count
            FROM cricket_player_data
            GROUP BY role;
        """,

        "Highest Individual Batting Score per Format": """
            SELECT format, MAX(highest_score) AS highest_score
            FROM (
                SELECT format, highest_score FROM all_batsmen_stats
                UNION ALL
                SELECT format, high_score AS highest_score FROM all_rounders_batting_stats
            ) AS combined_stats
            WHERE format IN ('Test', 'ODI', 'T20','IPL')
            GROUP BY format;
        """,

        "Cricket Series in 2024": """
            SELECT name AS series_name, series_type AS match_type, start_date
            FROM all_cricket_series
            WHERE STRFTIME('%Y', start_date) = '2024';
        """,

        "Really Good All-Rounders": """
            SELECT b.player_name, b.runs AS total_runs, w.wickets AS total_wickets, b.format
            FROM all_rounders_batting_stats b
            JOIN all_rounders_bowling_stats w
              ON b.player_id = w.player_id AND b.format = w.format
            WHERE b.runs > 1000 AND w.wickets > 50;
        """,

        "Player Match Counts and Batting Averages Across Formats (Min 20 Matches)": """
            WITH format_summary AS (
                SELECT player_name, format, SUM(matches) AS matches, AVG(average) AS batting_avg
                FROM Overall_batsman_stats
                WHERE format IN ('Test', 'ODI', 'T20')
                GROUP BY player_name, format
            ),
            pivoted AS (
                SELECT
                    player_name,
                    MAX(CASE WHEN format = 'Test' THEN matches END) AS matches_Test,
                    MAX(CASE WHEN format = 'ODI' THEN matches END) AS matches_ODI,
                    MAX(CASE WHEN format = 'T20' THEN matches_T20,
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
        """,

        "Comprehensive Player Performance Ranking": """
            WITH batting AS (
                SELECT player_id, player_name, SUM(runs) AS total_runs,
                       AVG(avg) AS batting_avg, AVG(strike_rate) AS strike_rate,
                       (SUM(runs) * 0.01) + (AVG(avg) * 0.5) + (AVG(strike_rate) * 0.3) AS batting_points
                FROM all_rounders_batting_stats
                GROUP BY player_id, player_name
            ),
            bowling AS (
                SELECT player_id, player_name, SUM(wickets) AS total_wickets,
                       AVG(avg) AS bowling_avg, AVG(eco) AS economy,
                       (SUM(wickets) * 2) + ((50 - AVG(avg)) * 0.5) + ((6 - AVG(eco)) * 2) AS bowling_points
                FROM all_rounders_bowling_stats
                GROUP BY player_id, player_name
            ),
            bat_left AS (
                SELECT b.player_id, b.player_name, b.total_runs, b.batting_avg, b.strike_rate,
                       bo.total_wickets, bo.bowling_avg, bo.economy,
                       b.batting_points, COALESCE(bo.bowling_points, 0) AS bowling_points
                FROM batting b
                LEFT JOIN bowling bo ON b.player_id = bo.player_id
            ),
            bowl_left AS (
                SELECT bo.player_id, bo.player_name, b.total_runs, b.batting_avg, b.strike_rate,
                       bo.total_wickets, bo.bowling_avg, bo.economy,
                       COALESCE(b.batting_points, 0) AS batting_points, bo.bowling_points
                FROM bowling bo
                LEFT JOIN batting b ON b.player_id = bo.player_id
            )
            SELECT *, (batting_points + bowling_points) AS total_points
            FROM bat_left
            UNION
            SELECT *, (batting_points + bowling_points) AS total_points
            FROM bowl_left
            ORDER BY total_points DESC;
        """
    }

    # ==========================
    # Helper function
    # ==========================
    def run_query(query: str) -> pd.DataFrame:
        """Execute SQL query and return results as DataFrame."""
        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error executing query: {e}")
            return pd.DataFrame()

    # ==========================
    # UI
    # ==========================
    st.title("CricBuzz SQL Query Explorer")

    query_choice = st.selectbox("Choose a query to execute:", list(QUERIES.keys()))

    st.subheader("Query to be executed:")
    st.code(QUERIES[query_choice], language="sql")

    if st.button("Run Query"):
        df = run_query(QUERIES[query_choice])
        if not df.empty:
            st.success("Query executed successfully ✅")
            st.dataframe(df)

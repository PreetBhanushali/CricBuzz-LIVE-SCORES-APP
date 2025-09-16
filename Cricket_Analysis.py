import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# Must be the first Streamlit command
# st.set_page_config(page_title="Cricket Analytics", layout="wide")


def app():

    # ---------------- Load Data ----------------
    batsmen = pd.read_csv("CSV FILES\Batsmen_stats.csv")
    allrounder_bat = pd.read_csv("CSV FILES\All Rounder Batting Stats.csv")
    bowlers = pd.read_csv("CSV FILES\Bowlers_stats.csv")
    allrounder_bowl = pd.read_csv("CSV FILES\All Rounder Bowling Stats.csv")

    # Ensure consistent column naming
    if "average" in batsmen.columns:
        batsmen.rename(columns={"average": "avg"}, inplace=True)
    if "average" in allrounder_bat.columns:
        allrounder_bat.rename(columns={"average": "avg"}, inplace=True)

    # Merge batting datasets
    batting_df = pd.concat([batsmen, allrounder_bat], ignore_index=True)

    # Merge bowling datasets
    bowling_df = pd.concat([bowlers, allrounder_bowl], ignore_index=True)

    # ---------------- Career Field Options ----------------
    batting_fields = ["innings", "runs", "balls_faced", "highest_score", "avg", "strike_rate",
                      "not_out", "fours", "sixes", "fifty_plus", "hundreds", "double_hundreds"]

    bowling_fields = ["innings", "balls", "runs", "maidens", "wickets", "avg", "eco", "sr",
                      "bbi", "bbm", "4w", "5w", "10w"]

    # ---------------- Tabs ----------------
    tab1, tab2 = st.tabs(["🏏 Batting", "🎯 Bowling"])

    # ---------------- Batting Section ----------------
    with tab1:
        st.header("Batting Leaderboard")

        career_field = st.selectbox("Select Career Field", batting_fields, key="batting_field")
        formats = batting_df["format"].dropna().unique().tolist()
        formats.sort()
        selected_format = st.selectbox("Select Format (optional)", ["All"] + formats, key="batting_format")

        df = batting_df.copy()

        # Apply format filter if selected
        if selected_format != "All":
            df = df[df["format"] == selected_format]

        # Group by player and sum the numeric fields
        top_df = df.groupby("player_name", as_index=False)[career_field].sum()
        top_df = top_df.sort_values(by=career_field, ascending=False).head(10)

        # Bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(top_df["player_name"], top_df[career_field], color="skyblue")
        ax.set_xlabel(career_field.capitalize())
        ax.set_ylabel("Player")
        ax.set_title(f"Top 10 Players by {career_field.capitalize()} ({selected_format})")
        ax.invert_yaxis()
        st.pyplot(fig)

    # ---------------- Bowling Section ----------------
    with tab2:
        st.header("Bowling Leaderboard")

        career_field = st.selectbox("Select Career Field", bowling_fields, key="bowling_field")
        formats = bowling_df["format"].dropna().unique().tolist()
        formats.sort()
        selected_format = st.selectbox("Select Format (optional)", ["All"] + formats, key="bowling_format")

        df = bowling_df.copy()

        # Apply format filter if selected
        if selected_format != "All":
            df = df[df["format"] == selected_format]

        # Group by player and sum the numeric fields
        top_df = df.groupby("player_name", as_index=False)[career_field].sum()
        top_df = top_df.sort_values(by=career_field, ascending=False).head(10)

        # Bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(top_df["player_name"], top_df[career_field], color="lightgreen")
        ax.set_xlabel(career_field.capitalize())
        ax.set_ylabel("Player")
        ax.set_title(f"Top 10 Players by {career_field.capitalize()} ({selected_format})")
        ax.invert_yaxis()
        st.pyplot(fig)


# Launcher
if __name__ == "__main__":
    app()



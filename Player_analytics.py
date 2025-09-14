import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Cricket Player Management", layout="wide")

def app():
    st.title("🏏 Cricket Player CRUD Application")

    # Load datasets
    players_file = "CSV FILES\Players_Data.csv"
    batsmen_file = "CSV FILES\Batsmen_stats.csv"

    if os.path.exists(players_file) and os.path.exists(batsmen_file):
        players_df = pd.read_csv(players_file)
        batsmen_df = pd.read_csv(batsmen_file)

        # Merge Players_Data.id with Batsmen_stats.player_id
        data = pd.merge(players_df, batsmen_df, left_on="id", right_on="player_id", how="left")

        # Sidebar Navigation
        crud_action = st.sidebar.radio("Select Action", ["Create", "Read", "Update", "Delete"])

        # CREATE
        if crud_action == "Create":
            st.subheader("➕ Add New Player")
            with st.form("create_form"):
                player_id = st.text_input("Player ID")  # will go to both id and player_id
                name = st.text_input("Name")
                battingStyle = st.selectbox("Batting Style", ["Right-hand bat", "Left-hand bat"])
                bowlingStyle = st.text_input("Bowling Style")
                role = st.selectbox("Role", ["BATSMAN", "BOWLER", "ALL ROUNDER"])
                team_name = st.text_input("Team Name")
                format_ = st.selectbox("Format", batsmen_df["format"].unique())
                runs = st.number_input("Runs", min_value=0)
                average = st.number_input("Average", min_value=0.0)
                strike_rate = st.number_input("Strike Rate", min_value=0.0)

                submitted = st.form_submit_button("Add Player")
                if submitted:
                    # Append new player to Players_Data
                    new_player = {
                        "id": player_id,
                        "name": name,
                        "battingStyle": battingStyle,
                        "bowlingStyle": bowlingStyle,
                        "role": role,
                        "team_name": team_name
                    }
                    players_df = pd.concat([players_df, pd.DataFrame([new_player])], ignore_index=True)

                    # Append new stats to Batsmen_stats
                    new_stats = {
                        "player_id": player_id,
                        "player_name": name,
                        "format": format_,
                        "runs": runs,
                        "average": average,
                        "strike_rate": strike_rate
                    }
                    batsmen_df = pd.concat([batsmen_df, pd.DataFrame([new_stats])], ignore_index=True)

                    players_df.to_csv(players_file, index=False)
                    batsmen_df.to_csv(batsmen_file, index=False)

                    st.success(f"✅ Player {name} added successfully!")

        # READ
        elif crud_action == "Read":
            st.subheader("📖 Player Records")
            st.dataframe(data)

        # UPDATE
        elif crud_action == "Update":
            st.subheader("✏️ Update Player Information")
            player_ids = players_df["id"].tolist()
            selected_id = st.selectbox("Select Player ID", player_ids)

            player_row = players_df[players_df["id"] == selected_id].iloc[0]
            stat_row = batsmen_df[batsmen_df["player_id"] == selected_id].iloc[0]

            with st.form("update_form"):
                name = st.text_input("Name", player_row["name"])
                battingStyle = st.text_input("Batting Style", player_row["battingStyle"])
                bowlingStyle = st.text_input("Bowling Style", player_row["bowlingStyle"])
                role = st.text_input("Role", player_row["role"])
                team_name = st.text_input("Team Name", player_row["team_name"])
                runs = st.number_input("Runs", value=int(stat_row["runs"]))
                average = st.number_input("Average", value=float(stat_row["average"]))
                strike_rate = st.number_input("Strike Rate", value=float(stat_row["strike_rate"]))

                submitted = st.form_submit_button("Update Player")
                if submitted:
                    # Update Players_Data
                    players_df.loc[players_df["id"] == selected_id, ["name", "battingStyle", "bowlingStyle", "role", "team_name"]] = [name, battingStyle, bowlingStyle, role, team_name]

                    # Update Batsmen_stats
                    batsmen_df.loc[batsmen_df["player_id"] == selected_id, ["runs", "average", "strike_rate"]] = [runs, average, strike_rate]

                    players_df.to_csv(players_file, index=False)
                    batsmen_df.to_csv(batsmen_file, index=False)

                    st.success(f"✅ Player {name} updated successfully!")

        # DELETE
        elif crud_action == "Delete":
            st.subheader("🗑️ Delete Player")
            player_ids = players_df["id"].tolist()
            selected_id = st.selectbox("Select Player ID to Delete", player_ids)

            if st.button("Delete Player"):
                players_df = players_df[players_df["id"] != selected_id]
                batsmen_df = batsmen_df[batsmen_df["player_id"] != selected_id]

                players_df.to_csv(players_file, index=False)
                batsmen_df.to_csv(batsmen_file, index=False)

                st.success(f"✅ Player with ID {selected_id} deleted successfully!")

    else:
        st.error("❌ Players_Data.csv or Batsmen_stats.csv not found!")

import streamlit as st
import pandas as pd
from pathlib import Path

# st.set_page_config(page_title="Cricket Player Profiles", layout="wide")

def app():

    # --- Helper utilities -------------------------------------------------
    def read_csv_robust(path: Path) -> pd.DataFrame:
        try:
            df = pd.read_csv(path)
            return df
        except FileNotFoundError:
            st.error(f"File not found: {path}")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Error reading {path}: {e}")
            return pd.DataFrame()

    def find_name_col(df: pd.DataFrame) -> str:
        candidates = [c for c in df.columns if c.lower() in ("player", "player_name", "name")]
        if candidates:
            return candidates[0]
        for c in df.columns:
            if 'name' in c.lower() or 'player' in c.lower():
                return c
        return df.columns[0] if len(df.columns) > 0 else None

    def find_format_col(df: pd.DataFrame) -> str:
        candidates = [c for c in df.columns if c.lower() == 'format']
        if candidates:
            return candidates[0]
        for c in df.columns:
            if 'format' in c.lower():
                return c
        return None

    def pivot_stats_for_player(df: pd.DataFrame, player_col: str, player_name: str, format_col: str) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame()
        filtered = df[df[player_col].astype(str).str.lower() == player_name.lower()].copy()
        if filtered.empty:
            return pd.DataFrame()
        # Drop ID column if present
        drop_cols = [c for c in filtered.columns if 'id' in c.lower()]
        filtered = filtered.drop(columns=drop_cols, errors='ignore')
        value_cols = [c for c in filtered.columns if c not in (player_col, format_col)]
        numeric_cols = []
        for c in value_cols:
            try:
                converted = pd.to_numeric(filtered[c], errors='coerce')
                if converted.notna().any():
                    numeric_cols.append(c)
            except Exception:
                continue
        if numeric_cols:
            pivot = filtered.groupby(format_col)[numeric_cols].agg(lambda s: s.astype(float).round(2).astype(object)).reset_index()
            pivot = pivot.set_index(format_col)
            return pivot
        else:
            grouped = filtered.groupby(format_col).agg(lambda s: ' | '.join(s.astype(str).unique()))
            return grouped

    def display_player_basic_info(players_df: pd.DataFrame, player_name: str):
        cols_required = ['id', 'name', 'battingStyle', 'bowlingStyle', 'role', 'team_name']
        col_map = {}
        for req in cols_required:
            match = None
            for c in players_df.columns:
                if c.lower() == req.lower():
                    match = c
                    break
            col_map[req] = match

        name_col = None
        for c in players_df.columns:
            if c.lower() in ('name', 'player', 'player_name'):
                name_col = c
                break
        if name_col is None:
            name_col = players_df.columns[0]

        filtered = players_df[players_df[name_col].astype(str).str.lower() == player_name.lower()]
        if filtered.empty:
            st.warning(f"No metadata found for player: {player_name}")
            return

        display_cols = [col_map[r] for r in cols_required if col_map[r] is not None]
        info_df = filtered[display_cols].drop_duplicates().reset_index(drop=True)
        info_df.columns = [c.replace('_', ' ').title() for c in info_df.columns]

        st.markdown("**Player Information**")
        for idx, row in info_df.iterrows():
            c1, c2, c3 = st.columns([1,1,1])
            with c1:
                st.markdown(f"**ID:** {row.get('Id', '')}")
            with c2:
                st.markdown(f"**Name:** {row.get('Name', '')}")
            with c3:
                st.markdown(f"**Team:** {row.get('Team Name', '')}")

            c4, c5 = st.columns([1,1])
            with c4:
                st.markdown(f"**Batting Style:** {row.get('Battingstyle', row.get('Batting Style', ''))}")
            with c5:
                st.markdown(f"**Bowling Style:** {row.get('Bowlingstyle', row.get('Bowling Style', ''))}")

            st.markdown(f"**Role:** {row.get('Role', '')}")
            st.markdown("---")

    @st.cache_data
    def load_all_data():
        datasets = {}
        datasets['batsmen'] = read_csv_robust('Batsmen_stats.csv')
        datasets['bowlers'] = read_csv_robust('Bowlers_stats.csv')
        datasets['allrounder_bat'] = read_csv_robust('All Rounder Batting Stats.csv')
        datasets['allrounder_bowl'] = read_csv_robust('All Rounder Bowling Stats.csv')
        datasets['players'] = read_csv_robust('Players_Data.csv')
        return datasets

    datasets = load_all_data()

    st.title("Cricket Player Profiles")
    st.markdown("Select a role and a player to view their profile and pivoted statistics.")

    role = st.selectbox("Select Role", options=["BATSMAN", "BOWLER", "ALL ROUNDER"], index=0)

    if role == 'BATSMAN':
        df_role = datasets['batsmen']
    elif role == 'BOWLER':
        df_role = datasets['bowlers']
    else:
        df_role = pd.concat([datasets['allrounder_bat'], datasets['allrounder_bowl']], ignore_index=True, sort=False)

    player_col = find_name_col(df_role) if not df_role.empty else None
    player_list = []
    if player_col:
        player_list = sorted(df_role[player_col].dropna().astype(str).unique(), key=lambda s: s.lower())

    if not player_list:
        st.warning("No players found for the selected role or data file is missing.")
        st.stop()

    player_name = st.selectbox("PlayerName", options=player_list)

    players_df = datasets['players']
    if players_df.empty:
        st.error("Players_Data.csv is missing or empty. Cannot display player metadata.")
    else:
        display_player_basic_info(players_df, player_name)

    st.markdown("## Statistics")

    format_col = find_format_col(df_role) if not df_role.empty else None

    if role == 'BATSMAN':
        stats_df = datasets['batsmen']
        p = pivot_stats_for_player(stats_df, player_col, player_name, format_col)
        if p.empty:
            st.info("No batting statistics available for this player in Batsmen_stats.csv")
        else:
            st.markdown("**Batting Stats (by Format)**")
            st.dataframe(p)

    elif role == 'BOWLER':
        stats_df = datasets['bowlers']
        p = pivot_stats_for_player(stats_df, player_col, player_name, format_col)
        if p.empty:
            st.info("No bowling statistics available for this player in Bowlers_stats.csv")
        else:
            st.markdown("**Bowling Stats (by Format)**")
            st.dataframe(p)

    else:  # ALL ROUNDER
        bat_df = datasets['allrounder_bat']
        bat_player_col = find_name_col(bat_df) if not bat_df.empty else None
        bat_format_col = find_format_col(bat_df) if not bat_df.empty else None
        pbat = pivot_stats_for_player(bat_df, bat_player_col, player_name, bat_format_col)
        if pbat.empty:
            st.info("No allrounder batting stats available for this player in All Rounder Batting Stats.csv")
        else:
            st.markdown("**All-Rounder Batting Stats (by Format)**")
            st.dataframe(pbat)

        st.markdown("---")

        bowl_df = datasets['allrounder_bowl']
        bowl_player_col = find_name_col(bowl_df) if not bowl_df.empty else None
        bowl_format_col = find_format_col(bowl_df) if not bowl_df.empty else None
        pbowl = pivot_stats_for_player(bowl_df, bowl_player_col, player_name, bowl_format_col)
        if pbowl.empty:
            st.info("No allrounder bowling stats available for this player in All Rounder Bowling Stats.csv")
        else:
            st.markdown("**All-Rounder Bowling Stats (by Format)**")
            st.dataframe(pbowl)

    st.markdown("---")

if __name__ == "__main__":
    app()






import streamlit as st
import pandas as pd

def app():
    st.title("Browse Data")
    
    # Define a dictionary to map user-friendly names to file paths
    data_files = {
        "All Rounder Batting Stats": "All Rounder Batting Stats.csv",
        "All Rounder Bowling Stats": "All Rounder Bowling Stats.csv",
        "All Teams": "All_teams.csv",
        "Batsmen Stats": "Batsmen_stats.csv",
        "Bowlers Stats": "Bowlers_stats.csv",
        "Cricket Series": "Cricket_Series.csv",
        "Players Data": "Players_Data.csv",
        "Venue Details": "Venue_details.csv",
        "Venue Information": "Venue_information.csv",
        "Overall Bowlers Stats": "Overall_Bowlers_stats.csv",
        "Overall Batsman Stats": "Overall_batsman_stats.csv",
    }
    
    # Create a selectbox for the user to choose a table
    selected_table = st.selectbox(
        "Select a table to view:",
        list(data_files.keys()),
        index=None,
        placeholder="Select a table...",
    )
    
    # Load and display the selected data
    if selected_table:
        file_path = data_files[selected_table]
        try:
            # Load the CSV file into a DataFrame
            df = pd.read_csv(file_path)
            st.markdown(f"### Showing data for: `{file_path}`")
            st.dataframe(df, use_container_width=True)
        except FileNotFoundError:
            st.error(f"File not found: {file_path}. Please make sure the file is uploaded.")
        except Exception as e:
            st.error(f"An error occurred while loading the data: {e}")





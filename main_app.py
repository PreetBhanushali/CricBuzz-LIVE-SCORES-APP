import streamlit as st
import live_matches,Browse_data,Player_analytics,Sql_Analysis_Exploration,Players_Profile,Cricket_Analysis

# Define the pages in a dictionary
pages = {
    "Live Scorecard": live_matches,
    "Player Analytics": Player_analytics,
    "Browse Data": Browse_data,
    "Sql_Analysis_Exploration": Sql_Analysis_Exploration,
    "Players_Profile":Players_Profile,
    "Cricket_Analysis":Cricket_Analysis
}
# Add a sidebar for navigation
st.sidebar.title("Cricket Dashboard")
selection = st.sidebar.radio("Go to", list(pages.keys()))

# Run the selected page
pages[selection].app()

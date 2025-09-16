import streamlit as st
import requests
import json

def app():
    st.title("Live Scorecard")

    # IMPORTANT: Replace "YOUR_RAPIDAPI_KEY_HERE" with your actual RapidAPI key.
    headers = {
	"x-rapidapi-key": "0fec7b9425mshbc167bba6885159p1b85d7jsna612b835a4f0",
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"

    @st.cache_data(ttl=60)
    def fetch_live_data():
        """Fetches live match data from the Cricbuzz API."""
        try:
            response = requests.get(url, headers=headers)
            # Check for a successful response (status code 200)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.HTTPError as errh:
            st.error(f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            st.error(f"Connection Error: {errc}")
        except requests.exceptions.Timeout as errt:
            st.error(f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            st.error(f"An unexpected error occurred: {err}")
        except json.JSONDecodeError:
            st.error("Error decoding JSON from API response.")
        return None

    live_data = fetch_live_data()

    if live_data and 'typeMatches' in live_data:
        for match_type in live_data['typeMatches']:
            st.subheader(f"🌐 {match_type['matchType']} Matches")
            if 'seriesMatches' in match_type:
                for series_match in match_type['seriesMatches']:
                    if 'seriesAdWrapper' in series_match and 'matches' in series_match['seriesAdWrapper']:
                        series_ad_wrapper = series_match['seriesAdWrapper']
                        series_name = series_ad_wrapper.get('seriesName', 'Unknown Series')
                        
                        for match in series_ad_wrapper['matches']:
                            with st.expander(f"**{series_name}: {match['matchInfo']['matchDesc']}**"):
                                # Extract basic match info
                                match_info = match.get('matchInfo', {})
                                match_score = match.get('matchScore', {})
                                
                                team1_name = match_info.get('team1', {}).get('teamName', 'N/A')
                                team2_name = match_info.get('team2', {}).get('teamName', 'N/A')
                                match_status = match_info.get('status', 'N/A')
                                city = match_info.get('venueInfo', {}).get('city', 'N/A')
                                ground = match_info.get('venueInfo', {}).get('ground', 'N/A')

                                st.write(f"**Match:** {team1_name} vs {team2_name}")
                                st.write(f"**Status:** {match_status}")
                                st.write(f"**Venue:** {ground}, {city}")
                                
                                # Display scores if available
                                if 'team1Score' in match_score:
                                    team1_score_data = match_score['team1Score'].get('inngs1', {})
                                    runs = team1_score_data.get('runs', '-')
                                    wickets = team1_score_data.get('wickets', '-')
                                    overs = team1_score_data.get('overs', '-')
                                    st.write(f"**{team1_name} Score:** {runs}/{wickets} ({overs} overs)")
                                
                                if 'team2Score' in match_score:
                                    team2_score_data = match_score['team2Score'].get('inngs1', {})
                                    runs = team2_score_data.get('runs', '-')
                                    wickets = team2_score_data.get('wickets', '-')
                                    overs = team2_score_data.get('overs', '-')
                                    st.write(f"**{team2_name} Score:** {runs}/{wickets} ({overs} overs)")
    else:
        st.warning("No live data available. Please check your API key and network connection.")


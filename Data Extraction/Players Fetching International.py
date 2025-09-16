import requests
import pandas as pd
import time
import os
from requests.exceptions import JSONDecodeError

# Define the API headers from the user's prompt
HEADERS = {
    # Using the API key from the user's code snippet
    "x-rapidapi-key": "d08ad5ed80mshfa4f1be24cd6ec6p1e36b5jsn47875e9c26c2",
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}
BASE_URL = "https://cricbuzz-cricket.p.rapidapi.com/teams/v1/{}/players"

# List of CSV files provided by the user. Updated to a single file.
CSV_FILES = [
    'all_teams.csv'
]

def get_teams_from_csvs(file_list):
    """
    Reads team data from a list of CSV files and consolidates them,
    filtering for 'international' teams.
    
    Args:
        file_list (list): A list of CSV file paths.
        
    Returns:
        list: A list of dictionaries, each containing 'teamId', 'teamName', and 'team_type'.
    """
    all_teams = []
    print("Reading team data from CSV files...")
    for file_name in file_list:
        try:
            df = pd.read_csv(file_name)

            # Check if the required columns exist
            if 'teamId' in df.columns and 'teamName' in df.columns and 'team_type' in df.columns:
                # Filter the DataFrame to include only international teams
                df_international = df[df['team_type'] == 'international']
                
                # Convert the filtered DataFrame to a list of dictionaries
                teams = df_international[['teamId', 'teamName', 'team_type']].to_dict('records')
                all_teams.extend(teams)
                print(f"Successfully read and filtered {len(teams)} international teams from {file_name}")
            else:
                print(f"Skipping {file_name}: Missing 'teamId', 'teamName', or 'team_type' columns.")
        except FileNotFoundError:
            print(f"File not found: {file_name}. Skipping...")
        except Exception as e:
            print(f"An error occurred while reading {file_name}: {e}")
    
    # Remove duplicates based on teamId
    unique_teams = list({team['teamId']: team for team in all_teams}.values())
    print(f"\nFound a total of {len(unique_teams)} unique international teams across all files.")
    return unique_teams

def fetch_players_for_team(team_id):
    """
    Fetches player data for a given teamId from the Cricbuzz API.
    
    Args:
        team_id (int or str): The ID of the team.
        
    Returns:
        dict: The JSON response data, or None if the request fails.
    """
    url = BASE_URL.format(team_id)
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except JSONDecodeError as e:
        # Specific handling for non-JSON responses
        print(f"Error fetching data for team ID {team_id}: Invalid JSON response. The API might be returning an error page or no data.")
        return None
    except requests.exceptions.RequestException as e:
        # General handling for other request-related errors
        print(f"Error fetching data for team ID {team_id}: {e}")
        return None

def process_players_data(players_list, team_name):
    """
    Processes the raw player list from the API response and formats it.
    
    Args:
        players_list (list): The 'player' array from the API response.
        team_name (str): The name of the team.
        
    Returns:
        list: A list of formatted player dictionaries.
    """
    processed_players = []
    current_role = None
    if not players_list:
        return []

    for player in players_list:
        # Check if the entry is a role header (no 'id' key)
        if 'id' not in player and 'name' in player:
            current_role = player['name']
        elif 'id' in player:
            # This is a player entry
            player_data = {
                'id': player.get('id'),
                'name': player.get('name'),
                'battingStyle': player.get('battingStyle', ''),
                'bowlingStyle': player.get('bowlingStyle', ''),
                'role': current_role,
                'team_name': team_name
            }
            processed_players.append(player_data)
            
    return processed_players

def main():
    """
    Main function to orchestrate the data scraping and file generation.
    """
    all_teams = get_teams_from_csvs(CSV_FILES)
    all_players_data = []

    print("\nStarting to fetch player data from API...")
    for team in all_teams:
        team_id = team['teamId']
        team_name = team['teamName']
        print(f"Fetching players for Team: {team_name} (ID: {team_id})...")
        
        api_data = fetch_players_for_team(team_id)
        
        if api_data and 'player' in api_data:
            players = process_players_data(api_data['player'], team_name)
            all_players_data.extend(players)
            print(f"  -> Found {len(players)} players for {team_name}.")
        else:
            print(f"  -> No player data found or error for {team_name}.")
            
        # Add a delay to avoid hitting API rate limits
        time.sleep(1) 

    if all_players_data:
        # Create a DataFrame from the collected data
        df_players = pd.DataFrame(all_players_data)
        
        # Define the output file name
        output_file = "cricket_player_data.csv"
        
        # Save the DataFrame to a single CSV file
        df_players.to_csv(output_file, index=False)
        print(f"\nData collection complete. Total players found: {len(all_players_data)}")
        print(f"All data has been saved to '{output_file}'.")
    else:
        print("\nNo player data was collected. The output file will not be created.")

if __name__ == "__main__":
    main()
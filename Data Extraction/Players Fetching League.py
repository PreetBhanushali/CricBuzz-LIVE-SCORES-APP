import requests
import pandas as pd
import time
import os
import json
from requests.exceptions import JSONDecodeError, RequestException

# --- Global Constants and Counters ---
HEADERS = {
    # It's a good practice to use an environment variable for a real project
    # For this example, we use the key directly as provided by the user
    "x-rapidapi-key": "d08ad5ed80mshfa4f1be24cd6ec6p1e36b5jsn47875e9c26c2",
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}
BASE_URL = "https://cricbuzz-cricket.p.rapidapi.com/teams/v1/{}/players"
API_CALL_COUNT = 0
MAX_RETRIES = 5
CACHE_DIR = "api_cache"
CSV_FILES = [
    'all_teams.csv'
]

# --- Cache Management Functions ---

def setup_cache_dir():
    """
    Ensures the cache directory exists.
    """
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def get_cached_data(team_id):
    """
    Tries to retrieve data from the local cache.
    
    Args:
        team_id (int or str): The ID of the team.
        
    Returns:
        dict or None: The cached data if found, otherwise None.
    """
    cache_path = os.path.join(CACHE_DIR, f"{team_id}.json")
    if os.path.exists(cache_path):
        print(f"  -> Data for team {team_id} found in cache. Using cached data.")
        with open(cache_path, 'r') as f:
            return json.load(f)
    return None

def save_data_to_cache(team_id, data):
    """
    Saves API response data to the local cache.
    
    Args:
        team_id (int or str): The ID of the team.
        data (dict): The JSON data to save.
    """
    cache_path = os.path.join(CACHE_DIR, f"{team_id}.json")
    with open(cache_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"  -> Data for team {team_id} saved to cache.")

# --- API & Data Handling Functions ---

def get_teams_from_csvs(file_list):
    """
    Reads team data from a list of CSV files and consolidates them,
    filtering for 'league' teams.
    
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
            if 'teamId' in df.columns and 'teamName' in df.columns and 'team_type' in df.columns:
                df_league = df[df['team_type'] == 'league']
                teams = df_league[['teamId', 'teamName', 'team_type']].to_dict('records')
                all_teams.extend(teams)
                print(f"Successfully read and filtered {len(teams)} league teams from {file_name}")
            else:
                print(f"Skipping {file_name}: Missing 'teamId', 'teamName', or 'team_type' columns.")
        except FileNotFoundError:
            print(f"File not found: {file_name}. Skipping...")
        except Exception as e:
            print(f"An error occurred while reading {file_name}: {e}")
    
    unique_teams = list({team['teamId']: team for team in all_teams}.values())
    print(f"\nFound a total of {len(unique_teams)} unique league teams across all files.")
    return unique_teams

def fetch_players_for_team(team_id, retries=0):
    """
    Fetches player data for a given teamId from the Cricbuzz API, with retry logic.
    
    Args:
        team_id (int or str): The ID of the team.
        retries (int): Current number of retries.
        
    Returns:
        dict: The JSON response data, or None if the request fails.
    """
    global API_CALL_COUNT
    url = BASE_URL.format(team_id)
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        API_CALL_COUNT += 1
        print(f"  -> API call successful. Total calls made this session: {API_CALL_COUNT}")
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        if http_err.response.status_code == 429:
            # Handle "Too Many Requests" error with exponential backoff
            if retries < MAX_RETRIES:
                wait_time = 2 ** retries  # Exponential backoff (1s, 2s, 4s, etc.)
                print(f"  -> Received 429 Too Many Requests. Waiting {wait_time}s before retry {retries + 1}/{MAX_RETRIES}.")
                time.sleep(wait_time)
                return fetch_players_for_team(team_id, retries + 1)
            else:
                print("  -> Max retries reached for 429 error. Skipping this team.")
                return None
        else:
            print(f"  -> HTTP error fetching data for team ID {team_id}: {http_err}")
            return None
    except (JSONDecodeError, RequestException) as err:
        print(f"  -> An error occurred for team ID {team_id}: {err}")
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
        if 'id' not in player and 'name' in player:
            current_role = player['name']
        elif 'id' in player:
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
    setup_cache_dir()
    all_teams = get_teams_from_csvs(CSV_FILES)
    all_players_data = []

    print("\nStarting to fetch player data from API or cache...")
    for team in all_teams:
        team_id = team['teamId']
        team_name = team['teamName']
        print(f"Processing Team: {team_name} (ID: {team_id})...")
        
        # 1. Try to get data from cache first
        api_data = get_cached_data(team_id)

        # 2. If not in cache, fetch from API
        if api_data is None:
            api_data = fetch_players_for_team(team_id)
            if api_data:
                save_data_to_cache(team_id, api_data)
        
        if api_data and 'player' in api_data:
            players = process_players_data(api_data['player'], team_name)
            all_players_data.extend(players)
            print(f"  -> Found {len(players)} players for {team_name}.")
        else:
            print(f"  -> No player data found or error for {team_name}. Skipping.")

    if all_players_data:
        df_players = pd.DataFrame(all_players_data)
        output_file = "cricket_player_league_data.csv"
        df_players.to_csv(output_file, index=False)
        print(f"\nData collection complete. Total players found: {len(all_players_data)}")
        print(f"All data has been saved to '{output_file}'.")
    else:
        print("\nNo player data was collected. The output file will not be created.")

if __name__ == "__main__":
    main()

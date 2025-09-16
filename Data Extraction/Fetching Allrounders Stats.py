import pandas as pd
import requests
import time
import sys
import os

def get_players_by_role_from_csv(file_path: str, role: str) -> pd.DataFrame:
    """
    Reads a CSV file from a specified file path, filters for players with a given role,
    and returns their IDs and names in a DataFrame.
    """
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' was not found.", file=sys.stderr)
        return pd.DataFrame()
        
    try:
        df = pd.read_csv(file_path)
        players_df = df[df['role'] == role][['id', 'name']]
        return players_df
    except Exception as e:
        print(f"Error processing CSV file: {e}", file=sys.stderr)
        return pd.DataFrame()

def fetch_player_bowling_stats(player_id: str, api_key: str, api_host: str) -> dict:
    """
    Fetches bowling statistics for a single player from the Cricbuzz API.
    """
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}/bowling"
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": api_host
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching bowling data for player ID {player_id}: {e}", file=sys.stderr)
        return {}

def fetch_player_batting_stats(player_id: str, api_key: str, api_host: str) -> dict:
    """
    Fetches batting statistics for a single player from the Cricbuzz API.
    """
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}/batting"
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": api_host
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching batting data for player ID {player_id}: {e}", file=sys.stderr)
        return {}

def parse_bowling_stats_json(json_data: dict, player_id: str, player_name: str) -> list[dict]:
    """
    Parses the JSON response and formats it into a list of dictionaries for bowling stats.
    """
    parsed_stats = []
    if not json_data or 'headers' not in json_data or 'values' not in json_data:
        return parsed_stats

    formats = json_data['headers'][1:]
    stats_map = {item['values'][0]: item['values'][1:] for item in json_data['values']}

    for i, fmt in enumerate(formats):
        row = {
            'player_id': player_id,
            'player_name': player_name,
            'format': fmt,
            'matches': stats_map.get('Matches', ['0'])[i] if i < len(stats_map.get('Matches', ['0'])) else '0',
            'innings': stats_map.get('Innings', ['0'])[i] if i < len(stats_map.get('Innings', ['0'])) else '0',
            'balls': stats_map.get('Balls', ['0'])[i] if i < len(stats_map.get('Balls', ['0'])) else '0',
            'runs': stats_map.get('Runs', ['0'])[i] if i < len(stats_map.get('Runs', ['0'])) else '0',
            'maidens': stats_map.get('Maidens', ['0'])[i] if i < len(stats_map.get('Maidens', ['0'])) else '0',
            'wickets': stats_map.get('Wickets', ['0'])[i] if i < len(stats_map.get('Wickets', ['0'])) else '0',
            'avg': stats_map.get('Avg', ['0.0'])[i] if i < len(stats_map.get('Avg', ['0.0'])) else '0.0',
            'eco': stats_map.get('Eco', ['0.0'])[i] if i < len(stats_map.get('Eco', ['0.0'])) else '0.0',
            'sr': stats_map.get('SR', ['0.0'])[i] if i < len(stats_map.get('SR', ['0.0'])) else '0.0',
            'bbi': stats_map.get('BBI', ['-/-'])[i] if i < len(stats_map.get('BBI', ['-/-'])) else '-/-',
            'bbm': stats_map.get('BBM', ['-/-'])[i] if i < len(stats_map.get('BBM', ['-/-'])) else '-/-',
            '4w': stats_map.get('4w', ['0'])[i] if i < len(stats_map.get('4w', ['0'])) else '0',
            '5w': stats_map.get('5w', ['0'])[i] if i < len(stats_map.get('5w', ['0'])) else '0',
            '10w': stats_map.get('10w', ['0'])[i] if i < len(stats_map.get('10w', ['0'])) else '0'
        }
        parsed_stats.append(row)
    return parsed_stats

def parse_batting_stats_json(json_data: dict, player_id: str, player_name: str) -> list[dict]:
    """
    Parses the JSON response and formats it into a list of dictionaries for batting stats.
    """
    parsed_stats = []
    if not json_data or 'headers' not in json_data or 'values' not in json_data:
        return parsed_stats
    
    formats = json_data['headers'][1:]
    stats_map = {item['values'][0]: item['values'][1:] for item in json_data['values']}

    for i, fmt in enumerate(formats):
        row = {
            'player_id': player_id,
            'player_name': player_name,
            'format': fmt,
            'matches': stats_map.get('Matches', ['0'])[i] if i < len(stats_map.get('Matches', ['0'])) else '0',
            'innings': stats_map.get('Innings', ['0'])[i] if i < len(stats_map.get('Innings', ['0'])) else '0',
            'not_out': stats_map.get('Not Outs', ['0'])[i] if i < len(stats_map.get('Not Outs', ['0'])) else '0',
            'runs': stats_map.get('Runs', ['0'])[i] if i < len(stats_map.get('Runs', ['0'])) else '0',
            'high_score': stats_map.get('Highest Score', ['0'])[i] if i < len(stats_map.get('Highest Score', ['0'])) else '0',
            'avg': stats_map.get('Avg', ['0.0'])[i] if i < len(stats_map.get('Avg', ['0.0'])) else '0.0',
            'strike_rate': stats_map.get('Strike Rate', ['0.0'])[i] if i < len(stats_map.get('Strike Rate', ['0.0'])) else '0.0',
            'hundreds': stats_map.get('100s', ['0'])[i] if i < len(stats_map.get('100s', ['0'])) else '0',
            'fifties': stats_map.get('50s', ['0'])[i] if i < len(stats_map.get('50s', ['0'])) else '0',
            'fours': stats_map.get('4s', ['0'])[i] if i < len(stats_map.get('4s', ['0'])) else '0',
            'sixes': stats_map.get('6s', ['0'])[i] if i < len(stats_map.get('6s', ['0'])) else '0',
            'ducks': stats_map.get('Ducks', ['0'])[i] if i < len(stats_map.get('Ducks', ['0'])) else '0'
        }
        parsed_stats.append(row)
    return parsed_stats

def main():
    """
    Main function to execute the data extraction process for all-rounders.
    """
    csv_file_path = "cricket_player_data.csv"
    
    print(f"Starting stats extraction for ALL ROUNDERs from '{csv_file_path}'...")
    
    # Get player IDs for all-rounders from the CSV file
    all_rounders_df = get_players_by_role_from_csv(csv_file_path, 'ALL ROUNDER')
    
    if all_rounders_df.empty:
        print("No all-rounders found in the CSV file or file not accessible. Exiting.", file=sys.stderr)
        return

    all_batting_stats = []
    all_bowling_stats = []
    
    # Your API key and host
    api_key = "a7d620e600msh1fd5e2619340345p161cb2jsn56f917c5665b"
    api_host = "cricbuzz-cricket.p.rapidapi.com"

    # Iterate through each all-rounder and fetch their data
    for index, row in all_rounders_df.iterrows():
        player_id = row['id']
        player_name = row['name']
        
        print(f"Fetching data for {player_name} (ID: {player_id})...")
        
        # Fetch and parse bowling stats
        bowling_json_data = fetch_player_bowling_stats(str(player_id), api_key, api_host)
        if bowling_json_data:
            parsed_bowling_data = parse_bowling_stats_json(bowling_json_data, str(player_id), player_name)
            all_bowling_stats.extend(parsed_bowling_data)
        
        # Fetch and parse batting stats
        batting_json_data = fetch_player_batting_stats(str(player_id), api_key, api_host)
        if batting_json_data:
            parsed_batting_data = parse_batting_stats_json(batting_json_data, str(player_id), player_name)
            all_batting_stats.extend(parsed_batting_data)
        
        # Pause to prevent hitting API rate limits
        time.sleep(5)

    if all_batting_stats:
        df_batting = pd.DataFrame(all_batting_stats)
        output_file_batting = 'all_rounders_batting_stats.csv'
        df_batting.to_csv(output_file_batting, index=False)
        print(f"Batting data extraction complete. Results saved to {output_file_batting}")
    else:
        print("No batting statistics were successfully retrieved.", file=sys.stderr)

    if all_bowling_stats:
        df_bowling = pd.DataFrame(all_bowling_stats)
        output_file_bowling = 'all_rounders_bowling_stats.csv'
        df_bowling.to_csv(output_file_bowling, index=False)
        print(f"Bowling data extraction complete. Results saved to {output_file_bowling}")
    else:
        print("No bowling statistics were successfully retrieved.", file=sys.stderr)

if __name__ == '__main__':
    main()

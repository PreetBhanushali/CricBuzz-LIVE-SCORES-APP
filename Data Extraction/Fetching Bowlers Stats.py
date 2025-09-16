import pandas as pd
import requests
import time
import sys
import os

def get_bowlers_ids_from_csv(file_path: str) -> pd.DataFrame:
    """
    Reads a CSV file from a specified file path, filters for players with the 'BOWLER' role,
    and returns their IDs and names in a DataFrame.
    """
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' was not found.", file=sys.stderr)
        return pd.DataFrame()
        
    try:
        df = pd.read_csv(file_path)
        bowlers_df = df[df['role'] == 'BOWLER'][['id', 'name']]
        return bowlers_df
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
        print(f"Error fetching data for player ID {player_id}: {e}", file=sys.stderr)
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

def main():
    """
    Main function to execute the data extraction process for bowlers.
    """
    csv_file_path = "cricket_player_data.csv"
    
    print(f"Starting bowling stats extraction from '{csv_file_path}'...")
    
    # Get player IDs for bowlers from the CSV file
    bowlers_df = get_bowlers_ids_from_csv(csv_file_path)
    
    if bowlers_df.empty:
        print("No bowlers found in the CSV file or file not accessible. Exiting.", file=sys.stderr)
        return

    all_players_stats = []
    
    # Your API key and host
    api_key = "db628101fcmshed571bf2e07f01ap1e0399jsn24eba9e2505c"
    api_host = "cricbuzz-cricket.p.rapidapi.com"

    # Iterate through each bowler and fetch their data
    for index, row in bowlers_df.iterrows():
        player_id = row['id']
        player_name = row['name']
        
        print(f"Fetching data for {player_name} (ID: {player_id})...")
        
        json_data = fetch_player_bowling_stats(str(player_id), api_key, api_host)
        
        if json_data:
            parsed_data = parse_bowling_stats_json(json_data, str(player_id), player_name)
            all_players_stats.extend(parsed_data)
        
        # Pause to prevent hitting API rate limits
        time.sleep(2)

    if all_players_stats:
        # Create a DataFrame from the collected data
        df_final = pd.DataFrame(all_players_stats)
        
        # Save to CSV
        output_file = 'all_bowlers_stats.csv'
        df_final.to_csv(output_file, index=False)
        print(f"Data extraction complete. Results saved to {output_file}")
    else:
        print("No statistics were successfully retrieved. The output CSV will not be created.", file=sys.stderr)

if __name__ == '__main__':
    main()

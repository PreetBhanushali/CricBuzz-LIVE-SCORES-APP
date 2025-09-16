import pandas as pd
import requests
import time
import sys
import os

def get_batsmen_ids_from_csv(file_path: str) -> pd.DataFrame:
    """
    Reads a CSV file from a specified file path, filters for players with the 'BATSMEN' role,
    and returns their IDs and names in a DataFrame.
    """
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' was not found.", file=sys.stderr)
        return pd.DataFrame()
        
    try:
        df = pd.read_csv(file_path)
        batsmen_df = df[df['role'] == 'BATSMEN'][['id', 'name']]
        return batsmen_df
    except Exception as e:
        print(f"Error processing CSV file: {e}", file=sys.stderr)
        return pd.DataFrame()

def fetch_player_stats(player_id: str, api_key: str, api_host: str) -> dict:
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
        print(f"Error fetching data for player ID {player_id}: {e}", file=sys.stderr)
        return {}

def parse_stats_json(json_data: dict, player_id: str, player_name: str) -> list[dict]:
    """
    Parses the JSON response and formats it into a list of dictionaries.
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
            'runs': stats_map.get('Runs', ['0'])[i] if i < len(stats_map.get('Runs', ['0'])) else '0',
            'balls_faced': stats_map.get('Balls', ['0'])[i] if i < len(stats_map.get('Balls', ['0'])) else '0',
            'highest_score': stats_map.get('Highest', ['0'])[i] if i < len(stats_map.get('Highest', ['0'])) else '0',
            'average': stats_map.get('Average', ['0.0'])[i] if i < len(stats_map.get('Average', ['0.0'])) else '0.0',
            'strike_rate': stats_map.get('SR', ['0.0'])[i] if i < len(stats_map.get('SR', ['0.0'])) else '0.0',
            'not_out': stats_map.get('Not Out', ['0'])[i] if i < len(stats_map.get('Not Out', ['0'])) else '0',
            'fours': stats_map.get('Fours', ['0'])[i] if i < len(stats_map.get('Fours', ['0'])) else '0',
            'sixes': stats_map.get('Sixes', ['0'])[i] if i < len(stats_map.get('Sixes', ['0'])) else '0',
            'fifty_plus': stats_map.get('50s', ['0'])[i] if i < len(stats_map.get('50s', ['0'])) else '0',
            'hundreds': stats_map.get('100s', ['0'])[i] if i < len(stats_map.get('100s', ['0'])) else '0',
            'double_hundreds': stats_map.get('200s', ['0'])[i] if i < len(stats_map.get('200s', ['0'])) else '0'
        }
        parsed_stats.append(row)
    return parsed_stats

def main():
    """
    Main function to execute the data extraction process.
    """
    csv_file_path = "cricket_player_data.csv"
    
    print(f"Starting data extraction from '{csv_file_path}'...")
    
    # Get player IDs for batsmen from the CSV file
    batsmen_df = get_batsmen_ids_from_csv(csv_file_path)
    
    if batsmen_df.empty:
        print("No batsmen found in the CSV file or file not accessible. Exiting.", file=sys.stderr)
        return

    all_players_stats = []
    
    # Replace with your actual API key and host
    api_key = "0fec7b9425mshbc167bba6885159p1b85d7jsna612b835a4f0"
    api_host = "cricbuzz-cricket.p.rapidapi.com"

    # Iterate through each batsman and fetch their data
    for index, row in batsmen_df.iterrows():
        player_id = row['id']
        player_name = row['name']
        
        print(f"Fetching data for {player_name} (ID: {player_id})...")
        
        json_data = fetch_player_stats(str(player_id), api_key, api_host)
        
        if json_data:
            parsed_data = parse_stats_json(json_data, str(player_id), player_name)
            all_players_stats.extend(parsed_data)
        
        # Pause to prevent hitting API rate limits
        time.sleep(0.5)

    if all_players_stats:
        # Create a DataFrame from the collected data
        df_final = pd.DataFrame(all_players_stats)
        
        # Save to CSV
        output_file = 'all_batsmen_stats.csv'
        df_final.to_csv(output_file, index=False)
        print(f"Data extraction complete. Results saved to {output_file}")
    else:
        print("No statistics were successfully retrieved. The output CSV will not be created.", file=sys.stderr)

if __name__ == '__main__':
    main()
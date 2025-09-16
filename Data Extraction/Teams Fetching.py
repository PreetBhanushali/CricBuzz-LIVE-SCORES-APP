import requests
import pandas as pd
import json
from io import StringIO

def get_teams_from_api(team_type):
    """
    Fetches cricket team data for a given team type from the Cricbuzz RapidAPI.

    Args:
        team_type (str): The type of cricket teams to fetch (e.g., 'international').

    Returns:
        list: A list of dictionaries containing team data, or None if the request fails.
    """
    # NOTE: You must replace "YOUR_RAPIDAPI_KEY_HERE" with your actual, valid key.
    # The key provided in the prompt is for demonstration purposes and will not work.
    url = f"https://cricbuzz-cricket.p.rapidapi.com/teams/v1/{team_type}"
    
    headers = {
	"x-rapidapi-key": "0f0637916emsh7de39c796d105c9p1a18d5jsn6321acab484a",
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        return data.get('list', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {team_type}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON for {team_type}: {e}")
        return None

def create_csv_from_teams(teams, file_prefix):
    """
    Creates a CSV file from a list of team dictionaries.
    
    Args:
        teams (list): A list of dictionaries, where each dictionary represents a team.
        file_prefix (str): The prefix for the output CSV file (e.g., 'international').
    """
    # Filter the list to only include teams with 'teamId', 'teamName', and 'teamSName'
    filtered_teams = [
        team for team in teams 
        if all(key in team for key in ['teamId', 'teamName', 'teamSName'])
    ]
    
    if not filtered_teams:
        print(f"No valid team data found for {file_prefix}.")
        return

    # Create a DataFrame from the filtered list of dictionaries
    df = pd.DataFrame(filtered_teams)
    
    # Select the required columns in the correct order
    df_final = df[['teamId', 'teamName', 'teamSName']]
    
    # Define the output filename
    output_filename = f"{file_prefix}_teams.csv"
    
    # Save the DataFrame to a CSV file
    df_final.to_csv(output_filename, index=False)
    
    print(f"Successfully created '{output_filename}' with {len(df_final)} teams.")


def main():
    """
    Main function to fetch data for various team types and create CSV files.
    """
    team_types = ['international', 'league', 'domestic', 'women']
    
    print("Starting data fetching and CSV creation process...")
    
    for team_type in team_types:
        print(f"\nProcessing team type: '{team_type}'")
        
        teams_data = get_teams_from_api(team_type)
        
        if teams_data:
            create_csv_from_teams(teams_data, team_type)
        else:
            print(f"Skipping CSV creation for {team_type} due to an error.")
            
    print("\nProcess completed.")


if __name__ == "__main__":
    main()

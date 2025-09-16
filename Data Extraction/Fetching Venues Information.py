import pandas as pd
import requests
from requests.exceptions import RequestException
import time

# This function reads the venue_details.csv and fetches venue data
# from the Cricbuzz API for each unique venue ID.
def get_venue_details(api_key, api_host):
    """
    Fetches detailed venue information from the Cricbuzz API.

    Args:
        api_key (str): The RapidAPI key for authentication.
        api_host (str): The RapidAPI host for the Cricbuzz API.

    Returns:
        list: A list of dictionaries, where each dictionary contains
              the detailed information for a venue.
    """
    try:
        # Read the venue_details.csv file using pandas.
        # This file is provided by the user and is located in the same directory.
        df_venues = pd.read_csv("venue_details.csv")
    except FileNotFoundError:
        print("Error: 'venue_details.csv' not found. Please ensure the file is in the correct path.")
        return []

    # Get a list of unique venue IDs from the 'id' column to avoid redundant API calls.
    venue_ids = df_venues['id'].unique()
    
    # Define the API headers for authentication.
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": api_host
    }
    
    # Initialize an empty list to store the venue data.
    venue_info_list = []
    
    # Loop through each unique venue ID.
    for venue_id in venue_ids:
        # Construct the API URL for the current venue ID.
        url = f"https://cricbuzz-cricket.p.rapidapi.com/venues/v1/{venue_id}"
        
        print(f"Fetching details for venue ID: {venue_id}...")
        
        try:
            # Make the GET request to the API.
            response = requests.get(url, headers=headers)
            
            # Raise an exception for bad status codes (4xx or 5xx).
            response.raise_for_status()
            
            # Parse the JSON response.
            venue_data = response.json()
            
            # Extract the required information and handle potential missing keys
            # by providing a default value (e.g., None).
            info = {
                "id": venue_id,
                "ground": venue_data.get("ground"),
                "city": venue_data.get("city"),
                "country": venue_data.get("country"),
                "timezone": venue_data.get("timezone"),
                "capacity": venue_data.get("capacity"),
                "ends": venue_data.get("ends"),
                "homeTeam": venue_data.get("homeTeam")
            }
            
            # Append the extracted info to our list.
            venue_info_list.append(info)
            
        except RequestException as e:
            # Print an error message if the API request fails.
            print(f"Error fetching data for venue ID {venue_id}: {e}")
        
        # Add a delay to avoid hitting the API rate limit.
        time.sleep(1)
            
    return venue_info_list

# Main execution block.
if __name__ == "__main__":
    # Your API key and host. NOTE: It's best practice to handle these
    # securely, e.g., using environment variables, but for this
    # self-contained script, we'll keep them here.
    RAPIDAPI_KEY = "d08ad5ed80mshfa4f1be24cd6ec6p1e36b5jsn47875e9c26c2"
    RAPIDAPI_HOST = "cricbuzz-cricket.p.rapidapi.com"
    
    # Call the function to get all venue details.
    all_venue_details = get_venue_details(RAPIDAPI_KEY, RAPIDAPI_HOST)
    
    # Check if any data was retrieved.
    if all_venue_details:
        # Create a pandas DataFrame from the list of dictionaries.
        df_venue_info = pd.DataFrame(all_venue_details)
        
        # Save the DataFrame to a new CSV file.
        # index=False prevents pandas from writing the DataFrame index as a column.
        df_venue_info.to_csv("venue_info.csv", index=False)
        
        print("\nSuccessfully created 'venue_info.csv' with the extracted venue data.")
    else:
        print("\nNo venue data was retrieved. The 'venue_info.csv' file was not created.")

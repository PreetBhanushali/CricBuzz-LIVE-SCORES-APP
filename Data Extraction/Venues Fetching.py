import requests
import pandas as pd
import os

# Define the file paths
input_csv_file = 'all_cricket_series.csv'
output_csv_file = 'venue_details.csv'

# Set up the API headers with the provided key and host
# Note: It's a good practice to handle sensitive information like API keys securely,
# for example, by storing them in environment variables.
headers = {
    "x-rapidapi-key": "b87c7076d0msh0b7df52da025facp1e3f86jsn77fa64563887",
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

# Base URL for the API endpoint
base_url = "https://cricbuzz-cricket.p.rapidapi.com/series/v1/{}/venues"

# Check if the input CSV file exists
if not os.path.exists(input_csv_file):
    print(f"Error: The file '{input_csv_file}' was not found.")
else:
    try:
        # Read the CSV file into a pandas DataFrame
        print(f"Reading data from '{input_csv_file}'...")
        series_df = pd.read_csv(input_csv_file)
        
        # Initialize a list to store all venue data
        all_venues = []
        
        # Iterate over the 'id' column of the DataFrame
        for series_id in series_df['id']:
            print(f"Fetching venue data for series ID: {series_id}")
            # Construct the API URL for the current series ID
            api_url = base_url.format(series_id)
            
            try:
                # Make the API request
                response = requests.get(api_url, headers=headers)
                
                # Check if the request was successful
                if response.status_code == 200:
                    data = response.json()
                    # Check if 'seriesVenue' data exists in the response
                    if 'seriesVenue' in data:
                        # Iterate through each venue in the list
                        for venue in data['seriesVenue']:
                            # Extract the required details and append to our list
                            venue_details = {
                                'id': venue.get('id'),
                                'ground': venue.get('ground'),
                                'city': venue.get('city'),
                                'country': venue.get('country')
                            }
                            all_venues.append(venue_details)
                    else:
                        print(f"No venue data found for series ID: {series_id}")
                else:
                    print(f"Failed to fetch data for series ID {series_id}. Status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"An error occurred during the request for series ID {series_id}: {e}")
        
        # Create a new DataFrame from the collected venue data
        if all_venues:
            venues_df = pd.DataFrame(all_venues)
            
            # Save the DataFrame to a new CSV file
            venues_df.to_csv(output_csv_file, index=False)
            print(f"\nSuccessfully saved all venue data to '{output_csv_file}'.")
        else:
            print("\nNo venue data was collected.")

    except pd.errors.EmptyDataError:
        print(f"Error: The file '{input_csv_file}' is empty.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

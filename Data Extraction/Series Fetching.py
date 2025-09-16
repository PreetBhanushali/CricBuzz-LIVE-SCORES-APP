import requests
import csv
from datetime import datetime

# Define the list of series types to fetch
series_types = ['international', 'league', 'domestic', 'women']

# Base URL and headers for the API request
base_url = "https://cricbuzz-cricket.p.rapidapi.com/series/v1/"
headers = {
    "x-rapidapi-key": "0f0637916emsh7de39c796d105c9p1a18d5jsn6321acab484a",
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

# List to store all series data from all types
all_series_data = []

print("Starting to fetch cricket series data...")

# Loop through each series type
for series_type in series_types:
    url = f"{base_url}{series_type}"
    print(f"\nFetching data for series type: '{series_type}' from URL: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        
        # Check if the API request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()
            
            # The series data is nested inside 'seriesMapProto'
            series_map_proto = data.get('seriesMapProto', [])
            
            # Use a variable to count the number of series fetched for the current type
            series_count = 0
            
            # Loop through the list of series maps
            for series_map in series_map_proto:
                series_list = series_map.get('series', [])
                
                # Check if any series data was found
                if series_list:
                    for series in series_list:
                        # Extract the required information for each series
                        series_id = series.get('id')
                        series_name = series.get('name')
                        
                        # The dates are in startDt and endDt and are timestamps in milliseconds
                        start_date_str = series.get('startDt')
                        end_date_str = series.get('endDt')
                        
                        start_date = None
                        if start_date_str:
                            # Convert the timestamp string to a datetime object
                            try:
                                start_date = datetime.fromtimestamp(int(start_date_str) / 1000).strftime('%Y-%m-%d')
                            except (ValueError, TypeError):
                                start_date = None # Handle cases of invalid timestamp
                        
                        end_date = None
                        if end_date_str:
                            # Convert the timestamp string to a datetime object
                            try:
                                end_date = datetime.fromtimestamp(int(end_date_str) / 1000).strftime('%Y-%m-%d')
                            except (ValueError, TypeError):
                                end_date = None # Handle cases of invalid timestamp

                        # Append the formatted data to our main list
                        all_series_data.append({
                            'id': series_id,
                            'name': series_name,
                            'start_date': start_date,
                            'end_date': end_date,
                            'series_type': series_type
                        })
                        series_count += 1
            
            print(f"Successfully fetched {series_count} series for '{series_type}'.")
            
        else:
            print(f"Error fetching data for '{series_type}'. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making the request for '{series_type}': {e}")
        
print("\nData fetching complete.")

# Define the name of the output CSV file
output_filename = 'all_cricket_series.csv'

# Check if we have any data to write
if all_series_data:
    # Define the column names for the CSV file
    csv_headers = ['id', 'name', 'start_date', 'end_date', 'series_type']
    
    try:
        # Open the CSV file in write mode
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Create a DictWriter object to write the data
            writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
            
            # Write the header row
            writer.writeheader()
            
            # Write the data rows
            writer.writerows(all_series_data)
        
        print(f"\nSuccessfully created and saved the file '{output_filename}'.")
        print(f"Total number of series written to the file: {len(all_series_data)}")
        
    except IOError as e:
        print(f"An I/O error occurred while writing the CSV file: {e}")
else:
    print(f"\nNo data was fetched to be written to a CSV file.")

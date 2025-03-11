import requests
import schedule
import time
from datetime import datetime

# Replace with your Google Apps Script web app URL
WEB_APP_URL = "https://script.google.com/macros/s/AKfycby9t3GdMJnQ24jYBM3LvGmTdy9pzNbqqbxi1lCGyrfzrXDacd9fvZBUu5DvxD-OrHi5Cg/exec"


# Function to fetch updated data
def fetch_updated_data(start_index=0, page_size=10):
    try:
        # Add pagination parameters to the API call
        params = {"startIndex": start_index, "pageSize": page_size}
        response = requests.get(WEB_APP_URL, params=params)
        response.raise_for_status()

        data = response.json()

        # Process updated files
        updated_files = data.get("data", [])
        for file in updated_files:
            process_file(file)

        # Check if there are more files to fetch
        if data.get("hasNext", False):
            next_start_index = start_index + page_size
            fetch_updated_data(start_index=next_start_index, page_size=page_size)

        print(
            f"Data fetch completed at {datetime.now()} with {len(updated_files)} files."
        )

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")


# Function to process each file and upsert into vector database
def process_file(file):
    try:
        print(f"Processing File: {file['name']} ({file['mimeType']})")

        # Safely handle 'content' key
        content = file.get("content")
        if content:
            print(f"Content: {content[:100]}...")  # Display first 100 characters
        else:
            print("Content is missing or empty.")

        # Call your vector database upsert method here
        upsert_to_vector_database(file)
    except KeyError as e:
        print(f"Missing key in file data: {e}")


# Mock function for vector database upsert
def upsert_to_vector_database(file):
    print(f"Upserting file ID {file['id']} to vector database...")
    # Add your vector database logic here
    pass


# Fetch data immediately upon starting
fetch_updated_data()

# Schedule the task every 10 minutes
schedule.every(1).minutes.do(fetch_updated_data)

# Keep the script running
print("Starting the data fetch scheduler...")
while True:
    schedule.run_pending()
    time.sleep(1)

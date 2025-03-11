import requests
from dotenv import load_dotenv
import os

load_dotenv(override=True)

# Replace with your API Key and Search Engine ID
API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")


# Function to perform a Google search
def google_search(query, api_key, search_engine_id, num_results=10):
    """
    Perform a Google search using the Custom Search JSON API.

    Args:
        query (str): Search query string.
        api_key (str): Google API key.
        search_engine_id (str): Custom Search Engine ID.
        num_results (int): Number of results to retrieve (max 10 per request).

    Returns:
        list: List of search result items.
    """
    # Base URL for Google Custom Search API
    url = "https://www.googleapis.com/customsearch/v1"

    # Parameters for the request
    params = {
        "q": query,  # Query term
        "key": api_key,  # API Key
        "cx": search_engine_id,  # Search Engine ID
        "num": min(num_results, 10),  # Max results per request
    }

    # Make the HTTP GET request
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        return data.get("items", [])
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return []


# Example usage
if __name__ == "__main__":
    search_query = "Yashed Thisara in WSO2"
    results = google_search(search_query, API_KEY, SEARCH_ENGINE_ID)

    if results:
        for index, result in enumerate(results):
            print(f"{index + 1}. {result['title']}")
            print(result["link"])
            print(result.get("snippet", "No description available"), "\n")
    else:
        print("No results found.")

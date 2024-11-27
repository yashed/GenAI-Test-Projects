import openai
import requests
from wikipedia.exceptions import PageError, DisambiguationError
import wikipedia
import os
from dotenv import load_dotenv

# Replace with your OpenAI API key and Google Custom Search API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")


# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY

# perform a Google search
def google_search(query, api_key, search_engine_id, num_results=5):
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,
        "cx": search_engine_id,
        "num": min(num_results, 10)
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data.get("items", [])
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return []

# fetch Wikipedia summary
def get_wikipedia_summary(person_name):
    
    try:
        return wikipedia.summary(person_name, sentences=5, auto_suggest=True)
    except PageError:
        return f"Sorry, I couldn't find a page for {person_name} on Wikipedia."
    except DisambiguationError as e:
        return f"The name {person_name} is ambiguous. Possible options are: {e.options}"

# generate response using GPT
def generate_person_details(person_name,company_name,job_title, google_results, wikipedia_info):
    
    # Prepare the context for GPT
    search_details = "\n".join(
        [f"- {result['title']}: {result.get('snippet', '')} ({result['link']})" for result in google_results]
    )

    prompt = (
    f"Provide a concise and accurate summary about {person_name}.\n"
    f"Working Company Name: {company_name}\n"
    f"Job Role of the person: {job_title}\n\n"
    f"Context: This information is for our company to better understand {person_name} as a potential lead interested in our product. "
    f"The goal is to summarize their professional background, current role, and publicly available insights in a straightforward and actionable manner to help our team prepare for meaningful engagement.\n\n"
    f"Google Search Results:\n{search_details}\n\n"
    f"Wikipedia Info:\n{wikipedia_info}\n\n"
    "Ensure the summary is clear, focused, and avoids repeating the same details. Highlight key points accurately, including relevant professional insights, potential interests, and any notable facts. "
    "Extract and list any social media links for the person in the following structure: prioritize LinkedIn if available, followed by other relevant platforms such as Twitter, GitHub, or personal websites. Include only one link per platform, ensuring correct formatting. "
    "Provide the social media links as a structured list after the summary."
)

    # Send the prompt to GPT
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that provides detailed information about people."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message["content"]

# Main script
if __name__ == "__main__":
    person_name = input("Enter the name of a person to search: ") 
    company_name = input("Enter the name of a company to search: ")
    job_title = input("Enter the job title of a person to search: ")
    # google_search = input("What you want to search in google: ")
    print(f"Fetching details for: {person_name}\n")

    # Wikipedia summary
    wikipedia_info = get_wikipedia_summary(person_name)
   
    # Google search results
    google_results = google_search(person_name, GOOGLE_API_KEY, SEARCH_ENGINE_ID)

    # Generate and display the detailed response
    if google_results:
        response = generate_person_details(person_name,company_name,job_title, google_results, wikipedia_info)
        print(response)
    else:
        print(f"No relevant results found for {person_name}.")

# Import required modules
import asyncio
import nest_asyncio
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PlaywrightLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from bs4 import BeautifulSoup

# Apply nest_asyncio to avoid async conflicts
nest_asyncio.apply()

# Define the URL
url = "https://www.imdb.com/list/ls566941243/"


# OpenAI API key
OPENAI_API_KEY = "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"

# Initialize ChatOpenAI instance
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-4-turbo")


# Function to scrape data asynchronously
async def scrape_imdb_page(url):
    # Load HTML content using PlaywrightLoader
    loader = PlaywrightLoader([url])
    docs = await loader.aload()
    return docs[0].page_content


# Main script
async def main():
    # Scrape the page content
    html_content = await scrape_imdb_page(url)

    # Save the HTML content to a text file
    with open("imdb_langchain_html.txt", "w", encoding="utf-8") as file:
        file.write(html_content)
    print("Page content has been saved to imdb_langchain_html.txt")

    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    titles = soup.find_all("h3")  # Extract movie titles
    paragraphs = soup.find_all("p")  # Extract movie descriptions

    # Combine extracted content
    extracted_content = []
    for title, paragraph in zip(titles, paragraphs):
        extracted_content.append(
            f"Title: {title.get_text(strip=True)}\nDescription: {paragraph.get_text(strip=True)}"
        )

    # Print extracted content
    for item in extracted_content:
        print(item)

    # Split documents using RecursiveCharacterTextSplitter for further processing
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    splits = splitter.create_documents([str(extracted_content)])
    print(f"Split documents: {splits}")


asyncio.run(main())

import openai
import wikipedia
from wikipedia.exceptions import PageError, DisambiguationError

openai.api_key = "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"


# Get the information from Wikipedia
person_name = "Elon Musk"
try:
    person_info = wikipedia.summary(person_name, sentences=5, auto_suggest=True)
except PageError:
    person_info = f"Sorry, I couldn't find a page for {person_name} on Wikipedia."
except DisambiguationError as e:
    person_info = f"The name {person_name} is ambiguous. Possible options are: {e.options}"

# Send the information to GPT API for processing
response = openai.ChatCompletion.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant who provides detailed information about people."},
        {"role": "user", "content": f"Tell me about {person_name}. Here's some information: {person_info}"}
    ]
)

# Output the response from the GPT model
print(response.choices[0].message["content"])

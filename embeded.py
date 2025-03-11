import openai


response = openai.Embedding.create(
    model="text-embedding-ada-002",  # "text-embedding-3-large" is deprecated; "text-embedding-ada-002" is recommended
    input="The food was delicious and the waiter...",
)

print(response)

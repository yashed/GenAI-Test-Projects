import openai

openai.api_key = "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"

response = openai.Embedding.create(
    model="text-embedding-ada-002",  # "text-embedding-3-large" is deprecated; "text-embedding-ada-002" is recommended
    input="The food was delicious and the waiter..."
)

print(response)

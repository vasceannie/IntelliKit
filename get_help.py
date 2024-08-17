import openai
import os

# Make sure to set your OpenAI API key as an environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

response = openai.Completion.create(
  engine="text-davinci-003",
  prompt="Analyze the following code...",
  max_tokens=100
)

print(response.choices[0].text)

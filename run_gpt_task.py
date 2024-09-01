import os
import time
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Function to handle retries in case of API rate limits or other temporary issues
def create_completion_with_retry(client, model, messages, retries=3):
    for i in range(retries):
        try:
            return client.chat.completions.create(model=model, messages=messages)
        except Exception as e:  # Generic exception handling
            if "Rate limit" in str(e):
                if i < retries - 1:
                    print(f"Rate limit error encountered, retrying in {2 ** i} seconds...")
                    time.sleep(2 ** i)  # Exponential backoff
                else:
                    raise
            else:
                print(f"An error occurred: {e}")
                exit(1)  # Exit the script if a general error occurs

# Check if the API key is loaded correctly
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY environment variable is not set.")
    exit(1)

# Define the directories to review
directories_to_review = [
    "backend/app/auth",
    "backend/app/validator",
    "backend/app",
    "backend/tests",
]

# Initialize an empty string to store all code content
code_content = ""
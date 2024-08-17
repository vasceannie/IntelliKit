import openai
import os
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Function to handle retries in case of API rate limits or other temporary issues
def create_completion_with_retry(client, model, messages, retries=3):
    for i in range(retries):
        try:
            return client.ChatCompletion.create(model=model, messages=messages)
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
    "app/api/endpoints",
    "app/core",
    "app/crud",
    "app/models",
    "app/schemas",
    "app/utils"
]

# Initialize an empty string to store all code content
code_content = ""

# Loop through each directory and read .py files
for directory in directories_to_review:
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if filename.endswith(".py"):
                filepath = os.path.join(directory, filename)
                with open(filepath, "r") as file:
                    code_content += f"\n\n# File: {filepath}\n\n" + file.read()
    else:
        print(f"Warning: Directory {directory} does not exist.")

if not code_content.strip():
    print("No code content found to review.")
    exit(1)

# Create a client instance
client = openai

# Step 1: Identify Bugs
try:
    bug_review = create_completion_with_retry(
        client,
        "gpt-4o-mini",
        [
            {"role": "system", "content": "You are an expert code reviewer."},
            {"role": "user", "content": f"Please review the following code and identify any bugs:\n\n{code_content}"}
        ]
    )
    print("Bugs and Issues:")
    print(bug_review.choices[0].message['content'])
except Exception as e:
    print(f"An error occurred during bug review: {e}")
    exit(1)  # Exit the script if an error occurs during bug review

# Step 2: Suggest Optimizations
try:
    optimization_review = create_completion_with_retry(
        client,
        "gpt-4o-mini",
        [
            {"role": "system", "content": "You are an expert code reviewer."},
            {"role": "user", "content": f"Please suggest optimizations for the following code:\n\n{code_content}"}
        ]
    )
    print("Optimizations:")
    print(optimization_review.choices[0].message['content'])
except Exception as e:
    print(f"An error occurred during optimization review: {e}")
    exit(1)  # Exit the script if an error occurs during optimization review

# Step 3: Generate Docstrings and Comments
try:
    docstring_review = create_completion_with_retry(
        client,
        "gpt-4o-mini",
        [
            {"role": "system", "content": "You are an expert Python developer."},
            {"role": "user", "content": f"Please add docstrings and comments to the following code:\n\n{code_content}"}
        ]
    )
    print("Docstrings and Comments:")
    print(docstring_review.choices[0].message['content'])
except Exception as e:
    print(f"An error occurred during docstring and comment generation: {e}")
    exit(1)  # Exit the script if an error occurs during docstring generation

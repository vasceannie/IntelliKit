import openai
import os
from dotenv import load_dotenv

load_dotenv()
# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

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
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "r") as file:
                code_content += f"\n\n# File: {filepath}\n\n" + file.read()

# Create a client instance
client = openai.Client()

# Step 1: Identify Bugs
bug_review = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are an expert code reviewer."},
        {"role": "user", "content": f"Please review the following code and identify any bugs:\n\n{code_content}"}
    ]
)

print("Bugs and Issues:")
print(bug_review.choices[0].message.content)

# Step 2: Suggest Optimizations
optimization_review = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are an expert code reviewer."},
        {"role": "user", "content": f"Please suggest optimizations for the following code:\n\n{code_content}"}
    ]
)

print("Optimizations:")
print(optimization_review.choices[0].message.content)

# Step 3: Generate Docstrings and Comments
docstring_review = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are an expert Python developer."},
        {"role": "user", "content": f"Please add docstrings and comments to the following code:\n\n{code_content}"}
    ]
)

print("Docstrings and Comments:")
print(docstring_review.choices[0].message.content)
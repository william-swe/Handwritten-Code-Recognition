import os
from openai import OpenAI
from utils import load_env_file

load_env_file()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

response = client.responses.create(
    model="o3",
    instructions="You are a coding assistant that talks like a pirate.",
    input="How do I check if a Python object is an instance of a class?",
)

print(response.output_text)
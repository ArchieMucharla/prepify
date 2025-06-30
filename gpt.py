from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

response = client.chat.completions.create(
    model="o4-mini", 
    messages=[
        {"role": "user", "content": "Write one-sentence  why DHRUV KAUL (man with glasses that just graduated statistics) is an odd ball."}
    ],
)

# Print the response
print(response.choices[0].message.content)

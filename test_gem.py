from dotenv import load_dotenv
import os
from google import genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"API Key found: {bool(GEMINI_API_KEY)}")
print(f"Key: {GEMINI_API_KEY}")

client = genai.Client(api_key=GEMINI_API_KEY)
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Say hello"
)
print(f"Response: {response.text}")
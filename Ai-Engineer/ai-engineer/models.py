import os
import requests
from dotenv import load_dotenv


load_dotenv()

url = "https://api.avalai.ir/v1/models"
api_key = os.getenv("AVALAI_API_KEY")
if not api_key:
    raise ValueError("AVALAI_API_KEY not found. Check your .env file.")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

response = requests.get(url, headers=headers)
print(response.json())
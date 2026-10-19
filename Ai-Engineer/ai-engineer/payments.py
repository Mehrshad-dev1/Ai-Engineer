import requests
from dotenv import load_dotenv
import os 


load_dotenv()
api_key = os.getenv("AVALAI_API_KEY")

url = "https://api.avalai.ir/user/v1/credit"
headers = {
 "Content-Type": "application/json",
 "Authorization": f"Bearer {api_key}"
}
response = requests.get(url, headers=headers)
# print(response.json())
print(response.json()['remaining_irt'])
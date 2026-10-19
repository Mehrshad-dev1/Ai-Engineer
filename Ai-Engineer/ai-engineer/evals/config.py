# config.py
import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

API_KEY = os.getenv("AVALAI_API_KEY")
if not API_KEY:
    raise ValueError("AVALAI_API_KEY not found. Check your .env file.")

CLIENT = OpenAI(api_key=API_KEY, base_url="https://api.avalai.ir/v1")
MODEL = "gpt-4o"  #MODEL = "gpt-6-luna"
MAX_STEPS = 4

CONTEXT_WINDOW = 128_000
COMPACT_THRESHOLD = 0.8


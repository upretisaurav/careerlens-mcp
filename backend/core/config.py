import os

from dotenv import load_dotenv

load_dotenv()

JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")

JSEARCH_BASE_URL = "https://jsearch.p.rapidapi.com"
JSEARCH_HEADERS = {
    "x-rapidapi-key": JSEARCH_API_KEY,
    "x-rapidapi-host": "jsearch.p.rapidapi.com",
}

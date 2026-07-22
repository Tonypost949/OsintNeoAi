import os
from dotenv import load_dotenv
load_dotenv()

llm_config = {
    "config_list": [
        {
            "model": "gemini-2.5-flash",
            "api_type": "google",
            "api_key": os.getenv("GEMINI_API_KEY")
        },
        {
            "model": "llama3",
            "api_key": "NotRequired",
            "base_url": "http://127.0.0.1:11434/v1"
        }
    ],
    "temperature": 0.7,
    "cache_seed": None
}

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
WISPR_API_KEY  = os.getenv("WISPR_API_KEY", "")

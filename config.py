import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Llama 4 Scout was retired on Groq; the course fix (starter repo PR #6) moves to gpt-oss-120b.
LLM_MODEL = "openai/gpt-oss-120b"
LOG_FILE = "logs/audit.jsonl"
VALID_TIERS = {"safe", "caution", "refuse"}

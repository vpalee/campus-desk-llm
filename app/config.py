import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from app.retrieval import ROOT

MODEL = 'gemma-4-E4B-it'
MIN_SCORE = 0.30  # selected on evaluation/dev.jsonl, not test.jsonl
MAX_ROUNDS = 4
MAX_TOOL_CALLS = 6


def configuration_ready() -> bool:
    load_dotenv(ROOT / '.env', override=False)
    key = os.getenv('OPENAI_API_KEY', '')
    url = urlparse(os.getenv('OPENAI_BASE_URL', ''))
    return bool(key and not key.startswith('replace-') and url.scheme == 'https'
                and url.hostname == 'llm.nat-d.uk' and not url.username and not url.password)

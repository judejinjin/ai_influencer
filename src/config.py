"""
Loads .env, exposes all API keys, defines paths and shared constants.
Supports 5 LLM providers: Gemini, OpenAI, Claude, OpenRouter, Grok.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── API Keys ──────────────────────────────────────────────────
GEMINI_KEY = os.getenv("GEMINI_KEY")
OPENAI_KEY = os.getenv("OPENAI_KEY")
CLAUDE_KEY = os.getenv("CLAUDE_KEY")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
GROK_KEY = os.getenv("GROK_KEY")

# ── Provider Configurations ───────────────────────────────────
PROVIDERS = {
    "gemini": {
        "key": GEMINI_KEY,
        "models": {
            "text": "gemini-2.0-flash",
            "text_fast": "gemini-2.0-flash",
            "video": "veo-3",
            "image": "imagen-3",
        },
    },
    "openai": {
        "key": OPENAI_KEY,
        "base_url": "https://api.openai.com/v1",
        "models": {
            "text": "gpt-4o",
            "text_fast": "gpt-4o-mini",
            "image": "dall-e-3",
        },
    },
    "claude": {
        "key": CLAUDE_KEY,
        "models": {
            "text": "claude-sonnet-4-20250514",
        },
    },
    "openrouter": {
        "key": OPENROUTER_KEY,
        "base_url": "https://openrouter.ai/api/v1",
        "models": {
            "text": "google/gemini-2.0-flash-exp:free",
        },
    },
    "grok": {
        "key": GROK_KEY,
        "base_url": "https://api.x.ai/v1",
        "models": {
            "text": "grok-3",
            "text_fast": "grok-3-mini",
        },
    },
}

# ── Default provider per task (can be overridden via CLI) ─────
DEFAULT_PROVIDERS = {
    "idea_generation": "gemini",
    "screenplay_writing": "claude",
    "news_analysis": "grok",
    "animation_video": "gemini",
    "animation_image": "gemini",
    "fallback": "openrouter",
}

# ── LLM Settings ──────────────────────────────────────────────
LLM_TEMPERATURE = 0.8
LLM_MAX_TOKENS = 4000

# ── Paths ─────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
GENERATED_DIR = DATA_DIR / "generated"
IDEAS_DIR = GENERATED_DIR / "ideas"
SCREENPLAYS_EN_DIR = GENERATED_DIR / "screenplays" / "en"
SCREENPLAYS_ES_DIR = GENERATED_DIR / "screenplays" / "es"
ANIMATIONS_DIR = GENERATED_DIR / "animations"
TEMPLATES_DIR = PROJECT_ROOT / "templates"

# ── Content Settings ──────────────────────────────────────────
CONTENT_PILLARS = [
    "comparison",
    "deep-dive",
    "regulation",
    "trending",
]
SUPPORTED_LANGUAGES = ["en", "es"]
DEFAULT_VIDEO_DURATION = 45

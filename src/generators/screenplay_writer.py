"""
Expands a content idea into a full bilingual (EN+ES) screenplay.
"""
import re
from datetime import datetime
from src.persona import SYSTEM_PROMPT_SCREENPLAY_WRITER
from src.llm_client import call_llm
from src.config import SCREENPLAYS_EN_DIR, SCREENPLAYS_ES_DIR


def write_screenplay(idea: dict, food_context: str = "",
                     regulation_context: str = "") -> dict:
    """
    Generate a bilingual screenplay from a content idea.

    Args:
        idea: Content idea dict (from idea_generator).
        food_context: Additional food facts for grounding.
        regulation_context: Additional regulation data.

    Returns:
        Dict with 'en' and 'es' screenplay text, and file paths.
    """
    user_prompt = f"""Expand this content idea into a full screenplay.

IDEA:
Title (EN): {idea.get('title_en', idea.get('title', 'Untitled'))}
Title (ES): {idea.get('title_es', '')}
Pillar: {idea.get('pillar', 'general')}
Hook (EN): {idea.get('hook_en', '')}
Hook (ES): {idea.get('hook_es', '')}
Key Message: {idea.get('key_message', '')}
Visual Elements: {', '.join(idea.get('visual_elements', []))}
Duration: {idea.get('duration_seconds', 45)} seconds
Props: {', '.join(idea.get('props_needed', []))}

ADDITIONAL CONTEXT:
{food_context}
{regulation_context}

Produce TWO complete screenplays:
1. === ENGLISH VERSION === (full screenplay in English)
2. === VERSIÓN EN ESPAÑOL === (full screenplay in Spanish — naturally written,
   NOT a literal translation)

Include all time codes, visual descriptions, voiceover lines, on-screen text,
shooting notes, props list, hashtags, and music suggestions.
"""

    response = call_llm(
        system_prompt=SYSTEM_PROMPT_SCREENPLAY_WRITER,
        user_prompt=user_prompt,
        task="screenplay_writing",
    )

    en_text, es_text = _split_bilingual(response)

    # Save files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = _slugify(idea.get("title_en", idea.get("title", "untitled")))

    en_path = SCREENPLAYS_EN_DIR / f"{slug}_{timestamp}.md"
    es_path = SCREENPLAYS_ES_DIR / f"{slug}_{timestamp}.md"
    en_path.parent.mkdir(parents=True, exist_ok=True)
    es_path.parent.mkdir(parents=True, exist_ok=True)
    en_path.write_text(en_text, encoding="utf-8")
    es_path.write_text(es_text, encoding="utf-8")

    return {
        "en": en_text,
        "es": es_text,
        "en_path": str(en_path),
        "es_path": str(es_path),
    }


def _split_bilingual(text: str) -> tuple[str, str]:
    """Split LLM output into English and Spanish sections."""
    parts = re.split(
        r"={3,}\s*(?:VERSIÓN EN ESPAÑOL|SPANISH VERSION|VERSIÓN EN ESPAÑOL)",
        text, maxsplit=1,
    )
    if len(parts) == 2:
        en_part = re.sub(r"={3,}\s*ENGLISH VERSION\s*={0,}", "", parts[0]).strip()
        es_part = parts[1].strip().lstrip("=").strip()
        return en_part, es_part
    return text.strip(), "[Spanish version not generated — re-run or translate manually]"


def _slugify(text: str) -> str:
    """Convert title to a filesystem-safe slug."""
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s-]+", "_", slug).strip("_")[:60]

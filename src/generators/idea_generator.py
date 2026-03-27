"""
Generates batches of content ideas using the LLM, persona, and research context.
"""
import json
from datetime import datetime
from src.persona import SYSTEM_PROMPT_IDEA_GENERATOR
from src.llm_client import call_llm, _strip_markdown_json
from src.config import IDEAS_DIR


def generate_ideas(
    count: int = 5,
    pillar: str = "all",
    food_context: str = "",
    news_context: str = "",
    regulation_context: str = "",
    provider: str = None,
) -> list[dict]:
    """
    Generate content ideas.

    Args:
        count: Number of ideas to generate.
        pillar: Content pillar filter ("all" or specific pillar).
        food_context: Injected food facts for grounding.
        news_context: Injected trending news for timeliness.
        regulation_context: Injected regulation data.
        provider: LLM provider override. Defaults to config.DEFAULT_PROVIDERS.

    Returns:
        List of idea dicts.
    """
    pillar_instruction = (
        f"Focus ONLY on the '{pillar}' content pillar."
        if pillar != "all"
        else "Mix ideas across all 4 content pillars."
    )

    user_prompt = f"""Generate {count} unique TikTok video ideas.

{pillar_instruction}

CONTEXT — USE THIS DATA to ground your ideas in real facts:

FOOD FACTS:
{food_context or "Use your general knowledge of healthy vs. processed foods."}

TRENDING NEWS:
{news_context or "No specific trending news provided — generate evergreen ideas."}

US REGULATION DATA:
{regulation_context or "Use your general knowledge of US food regulation issues."}

Return a JSON array of {count} idea objects.
"""

    response = call_llm(
        system_prompt=SYSTEM_PROMPT_IDEA_GENERATOR,
        user_prompt=user_prompt,
        task="idea_generation",
        provider=provider,
    )

    cleaned = _strip_markdown_json(response)
    ideas = json.loads(cleaned)
    if isinstance(ideas, dict) and "ideas" in ideas:
        ideas = ideas["ideas"]

    # Attach source context so downstream steps (screenplay writer) can use it
    for idea in ideas:
        if food_context:
            idea["_source_food_context"] = food_context
        if regulation_context:
            idea["_source_regulation_context"] = regulation_context

    # Save to disk
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = IDEAS_DIR / f"ideas_{timestamp}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(ideas, indent=2, ensure_ascii=False))

    return ideas

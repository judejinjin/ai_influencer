I'm a young beautiful sexy latina lady who loves cooking and eating healthy food.
I am Spanish and English bilingual.
I want to become an influencer on tiktok and other social media to promote healthy food and life styles.
I want to make sexy, funny and informative/educational short videos suitable for tiktok and other social media platforms.
All screenplays/manuscripts should be generated in both English and Spanish.

For the informative/educational part, I want to investigate/reveal how US regulations caused proliferation of toxic food addictives, ultra-processed food and educate my audience about it, how US regulations or directives caused rising percentage of obesity over the years.

In each of the videos, I want to compare healthy food vs. ultra-processed food, or focus on one healthy food to show how to get the most of it.

I also want to leverage off trending news(both positive and negative) regarding food safety when making new videos.

This project should produce scripts that can generate a repertoire of idea/screenplays based on current information, also scripts that can generate new ideas/screenplays and/or demonstration animations periodically in the future by searching trending news.

The demonstration animation is for guiding me on how to act, position, and shoot the video myself — it is NOT standalone published content, but a director's reference/storyboard animation.

Script that generates demonstration animation can be a separate/independent script.

This project should use python and virtual env.
LLM model API keys are provided in .env.

---

## Project Elaboration: Implementation Plan

### Overview

This project is an **AI-powered content pipeline** that generates TikTok/social-media screenplay ideas, scripts, and shooting-guide animations for a healthy-food influencer brand. It combines LLM-based content generation with real-time news monitoring to produce a steady stream of on-brand, engaging short-video concepts.

**Key traits**:
- **Bilingual output**: All screenplays and manuscripts are generated in both **English** and **Spanish** side by side, so the creator can choose which language to shoot in (or mix both for a wider audience).
- **Demonstration animations are shooting guides**: The animations are *not* published content — they are visual storyboard/director's references that show the creator how to position, act, move, and frame each shot.

---

### Project Structure

```
ai_influencer/
├── .env                        # API keys (Gemini, OpenAI, Claude, OpenRouter, Grok)
├── .gitignore
├── requirements.txt
├── project.md
├── src/
│   ├── __init__.py
│   ├── config.py               # Load .env, shared settings, persona definition
│   ├── persona.py              # Brand voice, persona traits, content guidelines
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── idea_generator.py   # Generate content ideas/concepts
│   │   ├── screenplay_writer.py # Turn ideas into bilingual screenplays (EN + ES)
│   │   └── animation_generator.py # Generate shooting guide animations (independent)
│   ├── research/
│   │   ├── __init__.py
│   │   ├── news_scraper.py     # Fetch trending food-safety news
│   │   ├── regulation_research.py # US food regulation facts & data
│   │   └── food_database.py    # Healthy vs. ultra-processed food knowledge base
│   ├── scheduler/
│   │   ├── __init__.py
│   │   └── periodic_runner.py  # Cron/schedule-based periodic generation
│   └── output/
│       ├── __init__.py
│       └── formatter.py        # Format screenplays into final output (markdown, JSON)
├── data/
│   ├── food_facts.json         # Curated healthy food facts & comparisons
│   ├── regulation_timeline.json # Timeline of US food regulation changes
│   └── generated/              # All generated content output goes here
│       ├── ideas/
│       ├── screenplays/
│       │   ├── en/             # English screenplays
│       │   └── es/             # Spanish screenplays
│       └── animations/         # Shooting guide animations (personal reference)
├── scripts/
│   ├── generate_repertoire.py  # One-shot: generate a batch of ideas & screenplays
│   ├── generate_from_trending.py # Fetch trending news → generate new content
│   └── generate_animation.py   # Standalone: generate demonstration animations
└── tests/
    └── ...
```

---

### Component Breakdown

#### 1. Persona & Brand Voice (`src/persona.py`)

Defines the influencer's identity so every piece of generated content stays on-brand:

- **Character**: Young, beautiful Latina woman passionate about cooking and healthy eating.
- **Languages**: Bilingual — fluent in both English and Spanish. Content can be delivered in either language or code-switched.
- **Tone**: Sexy, funny, approachable — but backed by real facts and education.
- **Content pillars**:
  1. Healthy food vs. ultra-processed food comparisons
  2. Deep dives into single healthy ingredients (how to buy, prep, cook, maximize nutrition)
  3. US food regulation exposés (FDA loopholes, banned-in-EU-but-legal-in-US additives, lobbying history)
  4. Trending food-safety news reactions/commentary
- **Format constraints**: Short-form video (15–60 seconds for TikTok, up to 90s for Reels/Shorts), hook in first 2 seconds, visual-first storytelling.

This persona definition is injected as a **system prompt** into every LLM call to maintain consistency.

The system prompt also instructs the LLM to produce every screenplay in **dual-language format** (English + Spanish), so each output contains both versions.

#### 2. Research Layer (`src/research/`)

##### `news_scraper.py` — Trending News Monitor
- Uses **NewsAPI**, **Google News RSS**, or **Bing News Search API** to find trending articles about:
  - Food safety recalls
  - FDA/USDA regulatory actions
  - Studies on ultra-processed food health effects
  - Viral food-related social media moments
- Filters and ranks results by relevance and recency.
- Returns structured data: headline, summary, source, date, relevance score.
- **Grok integration**: When generating ideas from trending news, the `generate_from_trending.py` script uses **Grok** (via xAI API) as the LLM — Grok has built-in real-time awareness of X/Twitter trends and current events, making it the best choice for timely news-reactive content.

##### `regulation_research.py` — US Food Regulation Knowledge
- Maintains a curated knowledge base of key US food regulation facts:
  - Timeline of deregulation events and their health impacts
  - List of additives banned in EU/other countries but allowed in the US (e.g., Red Dye 3, BHA/BHT, potassium bromate, azodicarbonamide)
  - Obesity statistics correlated with regulatory changes
  - Lobbying data and corporate influence on FDA decisions
- Provides context to the LLM for generating fact-based educational content.

##### `food_database.py` — Food Comparison Data
- Structured data on healthy foods and their ultra-processed counterparts:
  - Nutritional profiles, ingredient lists, health impacts
  - "Swap this for that" pairings (e.g., fresh salsa vs. store-bought with HFCS)
  - Tips on maximizing nutrition from whole foods (e.g., pair turmeric with black pepper for absorption)

#### 3. Content Generators (`src/generators/`)

##### `idea_generator.py` — Concept/Idea Generation
- **Input**: Content pillar selection, optional trending news item, optional specific food focus.
- **Process**: Constructs a prompt combining the persona, research context, and content guidelines → sends to LLM.
- **Output**: A batch of structured content ideas, each containing:
  - Title/hook
  - Content pillar category
  - Key message / educational takeaway
  - Suggested visual elements
  - Estimated duration
  - Trending relevance score (if news-based)

##### `screenplay_writer.py` — Full Bilingual Screenplay Generation
- **Input**: A content idea (from idea_generator or manual input).
- **Process**: Expands the idea into a detailed, time-coded screenplay **in both English and Spanish**:
  - **Hook** (0–2s): Attention-grabbing opening line or visual
  - **Setup** (2–10s): Context and framing
  - **Core content** (10–45s): The educational/comparison payload
  - **CTA/Punchline** (45–60s): Call to action, funny closer, or cliffhanger
- **Output**: Structured bilingual screenplay with:
  - Dialogue/voiceover lines in **English** and **Spanish** (with tone/delivery notes)
  - Visual/action descriptions (camera angles, props, food shots) — shared between both languages
  - On-screen text overlays in both languages
  - Sound/music cues
  - Hashtag suggestions (English + Spanish hashtags)
- **Output files**: Each screenplay produces two files — `{title}_EN.md` and `{title}_ES.md` — or a single combined file with both languages clearly sectioned.

##### `animation_generator.py` — Shooting Guide Animation (Independent Script)
- **Purpose**: Generate **shooting guide / storyboard animations** that visually demonstrate to the creator how to act, position herself, move, and frame each shot. These are personal reference videos — NOT published content.
- **What the animation shows**:
  - Character acting out each scene's blocking and movements
  - Camera angle/framing suggestions (close-up, wide, overhead, etc.)
  - Timing cues synced to the screenplay's time codes
  - Prop placement and food arrangement guidance
  - On-screen text placement indicators
- **Approach** (tiered — tries best option first, falls back):
  1. **Gemini Veo** (`veo-3` via `google-genai`) — **Primary**. Generates short AI video clips from text descriptions of each scene's blocking. Produces the most intuitive shooting guide since it shows realistic human movement and camera angles.
  2. **Gemini Imagen** (`imagen-3`) or **OpenAI DALL-E 3** — **Storyboard mode**. Generates one image per scene showing the body position, camera angle, and prop layout. MoviePy stitches them into a video with timing annotations.
  3. **Manim** (Python library) — **Fallback**. Programmatic stick-figure animation with camera framing overlays and timing markers. No API needed, works fully offline.
- **Output**: MP4/GIF files saved to `data/generated/animations/`, named to match their corresponding screenplay.
- This script is **fully independent** — it can be run standalone without the other generators.

#### 4. Orchestration Scripts (`scripts/`)

##### `generate_repertoire.py` — Initial Batch Generation
```
Usage: python scripts/generate_repertoire.py [--count 20] [--pillar all|comparison|deep-dive|regulation|trending] [--lang both|en|es]
```
- Generates a full repertoire of ideas and **bilingual screenplays** (English + Spanish by default).
- Draws from all content pillars, the food database, and regulation research.
- Outputs to `data/generated/ideas/` and `data/generated/screenplays/{en,es}/`.

##### `generate_from_trending.py` — News-Driven Generation
```
Usage: python scripts/generate_from_trending.py [--count 5] [--days 3]
```
- Fetches latest trending food-safety news.
- Generates new ideas and screenplays reacting to/leveraging those stories.
- Designed to be run periodically (daily/weekly via cron or scheduler).

##### `generate_animation.py` — Standalone Shooting Guide Animation
```
Usage: python scripts/generate_animation.py --screenplay <path> [--style storyboard|blocking|timing]
```
- Takes a screenplay and produces a visual shooting guide animation showing how to act, position, and frame each shot.
- Output is a personal director's reference — not for publishing.
- Fully independent from the other scripts.

#### 5. Periodic Scheduling (`src/scheduler/`)

- Uses Python's `schedule` library or system cron to automate:
  - **Daily**: Run `generate_from_trending.py` to capture fresh news.
  - **Weekly**: Generate a batch of new screenplay ideas to maintain the content calendar.
- Optionally sends notifications (email/Slack/Telegram) when new content is generated.

---

### Available APIs & Their Roles

You have **5 LLM/AI API keys** in `.env`. Here is exactly how each one is used:

| API Key | Service | Role in This Project | Python Library |
|---|---|---|---|
| `GEMINI_KEY` | Google Gemini | **Primary for idea generation & screenplays** (large context, fast, cheap). Also provides **Veo** for AI video generation → used for **shooting guide animations**. Also provides **Imagen** for storyboard frame images. | `google-genai` |
| `OPENAI_KEY` | OpenAI (GPT-4o) | **Secondary/fallback LLM** for creative writing. Also provides **DALL-E 3** for generating storyboard frame images as an alternative to Imagen. | `openai` |
| `CLAUDE_KEY` | Anthropic Claude | **Best for long-form screenplay writing** — excels at nuanced bilingual creative writing, cultural tone adaptation, and detailed instruction-following. Ideal for the screenplay writer module. | `anthropic` |
| `OPENROUTER_KEY` | OpenRouter | **Universal fallback / model switching** — routes to 100+ models (Llama, Mistral, etc.) via a single OpenAI-compatible API. Used when primary providers are down or rate-limited, or to A/B test different models. | `openai` (compatible endpoint) |
| `GROK_KEY` | xAI Grok | **Best for trending news analysis** — Grok has real-time X/Twitter integration and current events awareness. Ideal for the `generate_from_trending.py` pipeline to understand news context and generate timely reactions. | `openai` (compatible endpoint) |

#### How Each API is Called

| Provider | Base URL | Model Examples |
|---|---|---|
| Gemini | `google.genai` client | `gemini-2.0-flash`, `gemini-2.5-pro` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o`, `gpt-4o-mini` |
| Claude | `https://api.anthropic.com` | `claude-sonnet-4-20250514` |
| OpenRouter | `https://openrouter.ai/api/v1` | Any model via `openrouter/model-name` |
| Grok | `https://api.x.ai/v1` | `grok-3`, `grok-3-mini` |

#### Which API Produces the Shooting Guide Animation?

**Google Gemini** via its **Veo** video generation model is the primary option for generating demonstration/shooting-guide animations:

- **Veo** (`veo-3`) can generate short video clips from text prompts describing scenes, body positions, camera angles, and movements. This aligns perfectly with the shooting guide use case — you describe a scene's blocking and Veo renders a visual reference.
- **Imagen** (`imagen-3`) can generate individual storyboard frame images (one per scene/shot) showing body positions, camera framing, and prop placement.
- **Fallback**: If Veo output quality isn't sufficient, the project also supports **Manim** (local Python library) for programmatic stick-figure storyboard animations as originally planned.

The animation generator uses a **hybrid approach**:
1. LLM (any provider) parses the screenplay into shot-by-shot directing instructions
2. Gemini Veo generates video clips for each scene OR Gemini Imagen generates storyboard frames
3. MoviePy stitches clips/frames together with timing annotations
4. Fallback: Manim renders a programmatic stick-figure animation if AI generation is unavailable

---

### Tech Stack & Dependencies

| Component                    | Library / Service                           |
|------------------------------|---------------------------------------------|
| LLM — Gemini                 | `google-genai`                              |
| LLM — OpenAI                 | `openai`                                    |
| LLM — Claude                 | `anthropic`                                 |
| LLM — OpenRouter / Grok      | `openai` (compatible endpoint)              |
| Video generation (animation) | Gemini Veo via `google-genai`               |
| Image generation (storyboard)| Gemini Imagen or OpenAI DALL-E 3            |
| Animation fallback           | `manim` and/or `moviepy`, `Pillow`          |
| Environment management       | `python-dotenv`                             |
| News fetching                | `requests`, `feedparser` (Google News RSS)  |
| Web scraping (backup)        | `beautifulsoup4`, `httpx`                   |
| Scheduling                   | `schedule` or `APScheduler`                 |
| Data storage                 | JSON files (simple) or SQLite (if scaling)  |
| Output formatting            | `jinja2` (templated screenplay output)      |
| CLI interface                | `click`                                     |

### `requirements.txt`
```
google-genai>=1.0
openai>=1.30
anthropic>=0.30
python-dotenv>=1.0
requests>=2.31
beautifulsoup4>=4.12
httpx>=0.27
feedparser>=6.0
manim>=0.18
moviepy>=1.0
Pillow>=10.0
schedule>=1.2
jinja2>=3.1
click>=8.1
```

---

### `.env` File Format

```
GEMINI_KEY=AIza...
OPENAI_KEY=sk-proj-...
CLAUDE_KEY=sk-ant-api03-...
OPENROUTER_KEY=sk-or-v1-...
GROK_KEY=xai-...
```

---

### Detailed Implementation Plan

---

#### PHASE 1 — Project Foundation & Configuration

##### Step 1.1: Project Scaffolding

Create the full directory tree and initialize Python virtual environment.

```bash
# From /home/jude/ai_influener/
python3 -m venv venv
source venv/bin/activate

# Create directory structure
mkdir -p src/generators src/research src/scheduler src/output
mkdir -p data/generated/ideas data/generated/screenplays/en data/generated/screenplays/es
mkdir -p data/generated/animations
mkdir -p scripts tests templates

# Create __init__.py files
touch src/__init__.py src/generators/__init__.py src/research/__init__.py
touch src/scheduler/__init__.py src/output/__init__.py tests/__init__.py
```

Create `.gitignore`:
```
venv/
.env
__pycache__/
*.pyc
data/generated/
.DS_Store
```

##### Step 1.2: Dependencies (`requirements.txt`)

```
google-genai>=1.0
openai>=1.30
anthropic>=0.30
python-dotenv>=1.0
requests>=2.31
beautifulsoup4>=4.12
httpx>=0.27
feedparser>=6.0
manim>=0.18
moviepy>=1.0
Pillow>=10.0
schedule>=1.2
jinja2>=3.1
click>=8.1
```

Install: `pip install -r requirements.txt`

##### Step 1.3: Configuration (`src/config.py`)

Responsible for loading environment variables and defining shared constants for all 5 API providers.

```python
# src/config.py
"""
Loads .env, exposes all API keys, defines paths and shared constants.
Supports 5 LLM providers: Gemini, OpenAI, Claude, OpenRouter, Grok.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── API Keys ──────────────────────────────────────────────────
GEMINI_KEY = os.getenv("GEMINI_KEY")        # Google Gemini (primary LLM + Veo/Imagen)
OPENAI_KEY = os.getenv("OPENAI_KEY")        # OpenAI GPT-4o (secondary LLM + DALL-E)
CLAUDE_KEY = os.getenv("CLAUDE_KEY")        # Anthropic Claude (best for screenplays)
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")# OpenRouter (universal fallback)
GROK_KEY = os.getenv("GROK_KEY")            # xAI Grok (trending news analysis)

# ── Provider Configurations ───────────────────────────────────
PROVIDERS = {
    "gemini": {
        "key": GEMINI_KEY,
        "models": {
            "text": "gemini-2.5-pro",
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
            "text": "google/gemini-2.5-pro",  # or any model on OpenRouter
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
    "idea_generation": "gemini",      # Fast, big context, cheap
    "screenplay_writing": "claude",   # Best bilingual creative writing
    "news_analysis": "grok",          # Real-time awareness
    "animation_video": "gemini",      # Veo video generation
    "animation_image": "gemini",      # Imagen storyboard frames
    "fallback": "openrouter",         # Universal fallback
}

# ── LLM Settings ──────────────────────────────────────────────
LLM_TEMPERATURE = 0.8   # Creative but not hallucinating
LLM_MAX_TOKENS = 4096

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
    "comparison",     # Healthy food vs. ultra-processed food
    "deep-dive",      # Single healthy ingredient deep dive
    "regulation",     # US food regulation exposé
    "trending",       # Trending news reaction
]
SUPPORTED_LANGUAGES = ["en", "es"]
DEFAULT_VIDEO_DURATION = 45  # seconds
```

##### Step 1.4: Persona Definition (`src/persona.py`)

Contains the system prompt and brand guidelines injected into all LLM calls.

```python
# src/persona.py
"""
Defines the influencer persona, brand voice, and system prompts for LLM calls.
"""

PERSONA_BIO = {
    "character": "Young, beautiful, sexy Latina woman",
    "passions": ["cooking", "healthy eating", "educating about food safety"],
    "languages": ["English", "Spanish"],
    "tone": "Sexy, funny, approachable — backed by real facts and education",
    "platforms": ["TikTok", "Instagram Reels", "YouTube Shorts"],
}

# This is the master system prompt — injected into EVERY LLM call
SYSTEM_PROMPT_IDEA_GENERATOR = """
You are a creative content strategist for a TikTok influencer.

THE CREATOR:
- A young, beautiful, sexy Latina woman who loves cooking and eating healthy food.
- Bilingual: fluent in English and Spanish.
- Her brand is sexy, funny, and educational — she makes people laugh while
  teaching them serious truths about food safety and nutrition.

CONTENT PILLARS (choose from these for every idea):
1. COMPARISON: Healthy food vs. ultra-processed food (side-by-side reveals)
2. DEEP DIVE: Focus on one healthy ingredient — how to buy, prep, cook,
   maximize its nutrition
3. REGULATION EXPOSÉ: How US regulations (FDA, USDA) allow toxic additives
   banned in other countries; how deregulation fueled the obesity epidemic
4. TRENDING REACTION: React to/leverage breaking food-safety news

FORMAT RULES:
- Short-form video: 15–60 seconds (TikTok primary)
- Hook must land in the first 2 seconds
- Visual-first: every idea must describe what the VIEWER SEES
- Must be shootable by one person in a home kitchen with minimal props

OUTPUT FORMAT for each idea — return as JSON:
{
  "title_en": "...",
  "title_es": "...",
  "pillar": "comparison|deep-dive|regulation|trending",
  "hook_en": "First 2 seconds — what she says/does (English)",
  "hook_es": "First 2 seconds — what she says/does (Spanish)",
  "key_message": "The one educational takeaway",
  "visual_elements": ["list", "of", "key", "visuals"],
  "duration_seconds": 45,
  "props_needed": ["list", "of", "props"],
  "trending_relevance": "high|medium|low|none"
}
"""

SYSTEM_PROMPT_SCREENPLAY_WRITER = """
You are a screenplay writer for a TikTok influencer's short-form videos.

THE CREATOR:
- A young, beautiful, sexy Latina woman who loves cooking and eating healthy food.
- Bilingual: fluent in English and Spanish.
- Her brand is sexy, funny, and educational.

YOUR TASK:
Take a content idea and expand it into a fully detailed, time-coded screenplay.
You MUST produce TWO complete versions — one in ENGLISH and one in SPANISH.
Both versions share the same visual/action descriptions, but all spoken dialogue,
voiceover, and on-screen text must be naturally written in each language
(NOT a literal translation — adapt for cultural tone and idiom).

SCREENPLAY STRUCTURE:
[0-2s]  HOOK       — Attention-grabbing opening (visual + spoken)
[2-10s] SETUP      — Context, framing, show the problem or food
[10-45s] CORE      — Educational payload, comparison, or exposé
[45-60s] CTA       — Call to action, punchline, or cliffhanger

FOR EACH TIME BLOCK, INCLUDE:
- VISUAL: Exact description of what's on screen (camera angle, framing, action)
- VOICEOVER/DIALOGUE: Exact words spoken (with tone/delivery notes in parentheses)
- ON-SCREEN TEXT: Any text overlays
- SOUND/MUSIC: Audio cues

ALSO INCLUDE:
- PROPS NEEDED: Full list of everything needed to shoot
- SHOOTING NOTES: Tips on camera placement, lighting, angles
- HASHTAGS: 5-8 hashtags (both English and Spanish sets)
- MUSIC: Specific music mood or trending sound suggestion

Output the complete screenplay with clearly separated sections:
=== ENGLISH VERSION === and === VERSIÓN EN ESPAÑOL ===
"""

SYSTEM_PROMPT_ANIMATION_GUIDE = """
You are a video production director creating shot-by-shot storyboard descriptions.

Given a screenplay, produce a detailed SHOOTING GUIDE that describes:
- For each time block: exact body position, movement, facial expression
- Camera placement relative to the subject (distance, angle, height)
- Prop layout diagram (where each item sits on the counter/table)
- Transition cues between shots
- Timing (how many seconds to hold each position)

This is a PERSONAL REFERENCE for the creator — not published content.
Write it as clear, directive instructions ("Stand behind counter, lean forward
slightly, hold box in left hand at chest height, look directly at camera
with shocked expression").
"""
```

##### Step 1.5: Multi-Provider LLM Client (`src/llm_client.py`)

A unified client that can call **any of the 5 providers** depending on the task.
Each provider is initialized lazily (only when first used). Falls back to OpenRouter if the primary provider fails.

```python
# src/llm_client.py
"""
Multi-provider LLM client. Supports Gemini, OpenAI, Claude, OpenRouter, and Grok.
Each task routes to the best provider; falls back to OpenRouter on failure.
"""
from openai import OpenAI
from anthropic import Anthropic
from google import genai
from src.config import (
    PROVIDERS, DEFAULT_PROVIDERS, LLM_TEMPERATURE, LLM_MAX_TOKENS,
    GEMINI_KEY, OPENAI_KEY, CLAUDE_KEY, OPENROUTER_KEY, GROK_KEY,
)

# ── Lazy-initialized clients ──────────────────────────────────
_clients = {}

def _get_openai_compatible_client(provider: str) -> OpenAI:
    """Get or create an OpenAI-compatible client (works for OpenAI, OpenRouter, Grok)."""
    if provider not in _clients:
        cfg = PROVIDERS[provider]
        _clients[provider] = OpenAI(
            api_key=cfg["key"],
            base_url=cfg.get("base_url"),
        )
    return _clients[provider]

def _get_anthropic_client() -> Anthropic:
    if "claude" not in _clients:
        _clients["claude"] = Anthropic(api_key=CLAUDE_KEY)
    return _clients["claude"]

def _get_gemini_client():
    if "gemini" not in _clients:
        _clients["gemini"] = genai.Client(api_key=GEMINI_KEY)
    return _clients["gemini"]


# ── Main call function ────────────────────────────────────────
def call_llm(
    system_prompt: str,
    user_prompt: str,
    task: str = "idea_generation",
    provider: str = None,
    temperature: float = None,
    response_format: dict = None,
) -> str:
    """
    Send a prompt to the LLM and return the response text.

    Args:
        system_prompt: System instructions.
        user_prompt: User message.
        task: Task name (maps to DEFAULT_PROVIDERS for auto-routing).
        provider: Override provider ("gemini", "openai", "claude", "openrouter", "grok").
        temperature: Override temperature.
        response_format: JSON mode (OpenAI-compatible providers only).

    Returns:
        Response text from the LLM.
    """
    provider = provider or DEFAULT_PROVIDERS.get(task, "gemini")
    temp = temperature or LLM_TEMPERATURE

    try:
        if provider == "claude":
            return _call_claude(system_prompt, user_prompt, temp)
        elif provider == "gemini":
            return _call_gemini(system_prompt, user_prompt, temp)
        else:
            # OpenAI, OpenRouter, Grok — all OpenAI-compatible
            return _call_openai_compatible(
                provider, system_prompt, user_prompt, temp, response_format
            )
    except Exception as e:
        # Fallback to OpenRouter if primary provider fails
        fallback = DEFAULT_PROVIDERS.get("fallback", "openrouter")
        if provider != fallback:
            print(f"⚠️  {provider} failed ({e}), falling back to {fallback}")
            return _call_openai_compatible(
                fallback, system_prompt, user_prompt, temp, response_format
            )
        raise


# ── Provider-specific call implementations ────────────────────
def _call_gemini(system_prompt: str, user_prompt: str, temperature: float) -> str:
    """Call Google Gemini via the google-genai SDK."""
    client = _get_gemini_client()
    model = PROVIDERS["gemini"]["models"]["text"]
    response = client.models.generate_content(
        model=model,
        contents=user_prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            max_output_tokens=LLM_MAX_TOKENS,
        ),
    )
    return response.text

def _call_claude(system_prompt: str, user_prompt: str, temperature: float) -> str:
    """Call Anthropic Claude via the native SDK."""
    client = _get_anthropic_client()
    model = PROVIDERS["claude"]["models"]["text"]
    response = client.messages.create(
        model=model,
        max_tokens=LLM_MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
        temperature=temperature,
    )
    return response.content[0].text

def _call_openai_compatible(
    provider: str, system_prompt: str, user_prompt: str,
    temperature: float, response_format: dict = None,
) -> str:
    """Call any OpenAI-compatible API (OpenAI, OpenRouter, Grok)."""
    client = _get_openai_compatible_client(provider)
    model = PROVIDERS[provider]["models"]["text"]
    kwargs = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature or LLM_TEMPERATURE,
        "max_tokens": LLM_MAX_TOKENS,
    }
    if response_format:
        kwargs["response_format"] = response_format
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content
```

---

#### PHASE 2 — Content Idea Generator

##### Step 2.1: Idea Generator (`src/generators/idea_generator.py`)

```python
# src/generators/idea_generator.py
"""
Generates batches of content ideas using the LLM, persona, and research context.
"""
import json
from datetime import datetime
from pathlib import Path
from src.persona import SYSTEM_PROMPT_IDEA_GENERATOR
from src.llm_client import call_llm
from src.config import IDEAS_DIR, CONTENT_PILLARS

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
        provider: LLM provider override ("gemini", "openai", "claude",
                  "grok", "openrouter"). Defaults to config.DEFAULT_PROVIDERS.

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
        provider=provider,  # Routes to Gemini by default, or Grok for trending
    )

    ideas = json.loads(response)
    # Handle both {"ideas": [...]} and direct [...] formats
    if isinstance(ideas, dict) and "ideas" in ideas:
        ideas = ideas["ideas"]

    # Save to disk
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = IDEAS_DIR / f"ideas_{timestamp}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(ideas, indent=2, ensure_ascii=False))

    return ideas
```

**How it works**:
1. Receives optional context from the research layer (food facts, news, regulation data).
2. Builds a user prompt specifying how many ideas and which pillar.
3. Sends system prompt (persona) + user prompt to LLM.
4. Parses the JSON response into structured idea objects.
5. Saves the batch to `data/generated/ideas/` with a timestamp.

##### Step 2.2: Screenplay Writer (`src/generators/screenplay_writer.py`)

```python
# src/generators/screenplay_writer.py
"""
Expands a content idea into a full bilingual (EN+ES) screenplay.
"""
import re
from datetime import datetime
from pathlib import Path
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

    # Claude is the default for screenplay writing (best bilingual creative output)
    response = call_llm(
        system_prompt=SYSTEM_PROMPT_SCREENPLAY_WRITER,
        user_prompt=user_prompt,
        task="screenplay_writing",  # Routes to Claude by default
    )

    # Split response into EN and ES sections
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

    return {"en": en_text, "es": es_text, "en_path": str(en_path), "es_path": str(es_path)}


def _split_bilingual(text: str) -> tuple[str, str]:
    """Split LLM output into English and Spanish sections."""
    # Try splitting on the section markers
    parts = re.split(r"={3,}\s*(?:VERSIÓN EN ESPAÑOL|SPANISH VERSION)", text, maxsplit=1)
    if len(parts) == 2:
        en_part = re.sub(r"={3,}\s*ENGLISH VERSION\s*={0,}", "", parts[0]).strip()
        es_part = parts[1].strip().lstrip("=").strip()
        return en_part, es_part
    # Fallback: return the whole thing as EN, note missing ES
    return text.strip(), "[Spanish version not generated — re-run or translate manually]"


def _slugify(text: str) -> str:
    """Convert title to a filesystem-safe slug."""
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s-]+", "_", slug).strip("_")[:60]
```

**How it works**:
1. Takes a structured idea dict and optional grounding context.
2. Constructs a detailed prompt asking for two complete screenplays (EN + ES).
3. Parses the LLM response, splitting it into English and Spanish sections.
4. Saves each version to its respective language folder.
5. Returns both texts and their file paths.

---

#### PHASE 3 — Research Layer (Data & News)

##### Step 3.1: Food Database (`src/research/food_database.py`)

```python
# src/research/food_database.py
"""
Provides curated food comparison data and healthy ingredient facts.
Loads from data/food_facts.json and offers lookup/random selection.
"""
import json
import random
from src.config import DATA_DIR

FOOD_FACTS_PATH = DATA_DIR / "food_facts.json"

def load_food_facts() -> list[dict]:
    """Load the full food facts database."""
    if not FOOD_FACTS_PATH.exists():
        return _get_default_food_facts()
    return json.loads(FOOD_FACTS_PATH.read_text(encoding="utf-8"))

def get_random_comparisons(count: int = 3) -> list[dict]:
    """Return random healthy vs. processed food comparisons."""
    facts = load_food_facts()
    comparisons = [f for f in facts if f.get("type") == "comparison"]
    return random.sample(comparisons, min(count, len(comparisons)))

def get_random_deep_dives(count: int = 3) -> list[dict]:
    """Return random single-ingredient deep dive topics."""
    facts = load_food_facts()
    deep_dives = [f for f in facts if f.get("type") == "deep-dive"]
    return random.sample(deep_dives, min(count, len(deep_dives)))

def format_for_prompt(facts: list[dict]) -> str:
    """Format food facts into a string suitable for LLM prompt injection."""
    lines = []
    for f in facts:
        if f["type"] == "comparison":
            lines.append(
                f"• HEALTHY: {f['healthy_option']} vs. "
                f"PROCESSED: {f['processed_option']} — {f['key_fact']}"
            )
        elif f["type"] == "deep-dive":
            lines.append(
                f"• INGREDIENT: {f['ingredient']} — {f['key_fact']} "
                f"(Tip: {f['nutrition_tip']})"
            )
    return "\n".join(lines)

def _get_default_food_facts() -> list[dict]:
    """Hardcoded seed data — written to disk on first run."""
    # ... (see data/food_facts.json schema below)
```

**`data/food_facts.json` schema** — seed file to create:

```json
[
  {
    "type": "comparison",
    "healthy_option": "Fresh homemade salsa (tomatoes, onion, cilantro, lime)",
    "processed_option": "Store-bought salsa (high fructose corn syrup, artificial colors)",
    "key_fact": "Store-bought salsa can contain up to 4g added sugar per serving",
    "visual_idea": "Side-by-side ingredient lists — 5 ingredients vs. 25"
  },
  {
    "type": "comparison",
    "healthy_option": "Steel-cut oats with fresh berries",
    "processed_option": "Instant flavored oatmeal packets",
    "key_fact": "Instant packets contain up to 12g added sugar and artificial flavors",
    "visual_idea": "Pour packets side by side, read ingredients aloud"
  },
  {
    "type": "deep-dive",
    "ingredient": "Turmeric",
    "key_fact": "Curcumin (active compound) has powerful anti-inflammatory properties",
    "nutrition_tip": "Pair with black pepper to increase absorption by 2000%",
    "visual_idea": "Sprinkle turmeric + black pepper into a golden milk recipe"
  },
  {
    "type": "deep-dive",
    "ingredient": "Avocado",
    "key_fact": "Contains 20+ vitamins and minerals, healthy monounsaturated fats",
    "nutrition_tip": "Add a squeeze of lime to slow oxidation and boost vitamin C pairing",
    "visual_idea": "Cut open a perfect avocado, show ripeness test trick"
  }
]
```

This file should be seeded with **30–50 entries** across both types. The LLM can be used to help generate the initial seed data, then human-reviewed for accuracy.

##### Step 3.2: US Food Regulation Data (`src/research/regulation_research.py`)

```python
# src/research/regulation_research.py
"""
Provides curated US food regulation facts, timelines, and banned-additive data.
Loads from data/regulation_timeline.json.
"""
import json
import random
from src.config import DATA_DIR

REGULATION_PATH = DATA_DIR / "regulation_timeline.json"

def load_regulation_data() -> dict:
    """Load the full regulation dataset."""
    if not REGULATION_PATH.exists():
        return _get_default_regulation_data()
    return json.loads(REGULATION_PATH.read_text(encoding="utf-8"))

def get_banned_additives(count: int = 5) -> list[dict]:
    """Return additives banned elsewhere but legal in the US."""
    data = load_regulation_data()
    additives = data.get("banned_additives", [])
    return random.sample(additives, min(count, len(additives)))

def get_timeline_events(count: int = 5) -> list[dict]:
    """Return key regulatory timeline events."""
    data = load_regulation_data()
    events = data.get("timeline", [])
    return random.sample(events, min(count, len(events)))

def get_obesity_stats() -> list[dict]:
    """Return obesity statistics over time."""
    data = load_regulation_data()
    return data.get("obesity_stats", [])

def format_for_prompt(additives: list = None, events: list = None,
                      stats: list = None) -> str:
    """Format regulation data into an LLM-injectable string."""
    lines = []
    if additives:
        lines.append("ADDITIVES BANNED IN OTHER COUNTRIES BUT LEGAL IN US:")
        for a in additives:
            lines.append(
                f"  • {a['name']}: {a['used_in']} — "
                f"Banned in: {', '.join(a['banned_in'])} — "
                f"Health concern: {a['health_concern']}"
            )
    if events:
        lines.append("\nKEY REGULATORY EVENTS:")
        for e in events:
            lines.append(f"  • {e['year']}: {e['event']} — Impact: {e['impact']}")
    if stats:
        lines.append("\nUS OBESITY RATES OVER TIME:")
        for s in stats:
            lines.append(f"  • {s['year']}: {s['rate']}% (adults), {s.get('children_rate', 'N/A')}% (children)")
    return "\n".join(lines)
```

**`data/regulation_timeline.json` schema** — seed file to create:

```json
{
  "banned_additives": [
    {
      "name": "Red Dye 3 (Erythrosine)",
      "used_in": "Candy, baked goods, maraschino cherries",
      "banned_in": ["EU (partially)", "Austria", "Norway"],
      "health_concern": "Linked to thyroid tumors in animal studies; FDA acknowledged carcinogenicity in 1990 but only banned in cosmetics",
      "year_concern_raised": 1990
    },
    {
      "name": "Potassium Bromate",
      "used_in": "Bread, flour, baked goods",
      "banned_in": ["EU", "UK", "Canada", "Brazil", "China"],
      "health_concern": "Classified as possibly carcinogenic (Group 2B) by IARC",
      "year_concern_raised": 1999
    },
    {
      "name": "BHA (Butylated Hydroxyanisole)",
      "used_in": "Cereals, snack foods, chewing gum, butter",
      "banned_in": ["EU (restricted)", "Japan"],
      "health_concern": "Reasonably anticipated to be a human carcinogen (NTP)",
      "year_concern_raised": 2011
    },
    {
      "name": "Azodicarbonamide",
      "used_in": "Bread (as dough conditioner) — also used in yoga mats/shoe soles",
      "banned_in": ["EU", "Australia", "Singapore"],
      "health_concern": "Breaks down into semicarbazide (possible carcinogen) during baking",
      "year_concern_raised": 2005
    },
    {
      "name": "Titanium Dioxide (E171)",
      "used_in": "Candy, coffee creamer, frosting, supplements",
      "banned_in": ["EU (banned 2022)"],
      "health_concern": "Potential genotoxicity — can damage DNA per EFSA assessment",
      "year_concern_raised": 2021
    }
  ],
  "timeline": [
    {
      "year": 1958,
      "event": "Food Additives Amendment — GRAS (Generally Recognized As Safe) loophole created",
      "impact": "Companies can self-certify ingredients as safe WITHOUT FDA review"
    },
    {
      "year": 1977,
      "event": "McGovern Report recommends reducing sugar/fat in American diet",
      "impact": "Food industry lobbying weakened final guidelines — focus shifted to low-fat (which led to added sugar)"
    },
    {
      "year": 1992,
      "event": "USDA Food Pyramid released",
      "impact": "Heavily influenced by grain/dairy industry lobbying — recommended 6-11 servings of grains daily"
    },
    {
      "year": 1996,
      "event": "GRAS self-affirmation process formalized",
      "impact": "Companies no longer need to notify FDA before adding new chemicals to food"
    },
    {
      "year": 2015,
      "event": "FDA removes trans fats (partially hydrogenated oils) from GRAS list",
      "impact": "Took decades of evidence — shows how slow the US system is to act"
    }
  ],
  "obesity_stats": [
    {"year": 1960, "rate": 13.4, "children_rate": 5.0},
    {"year": 1980, "rate": 15.0, "children_rate": 5.5},
    {"year": 1994, "rate": 22.5, "children_rate": 10.0},
    {"year": 2000, "rate": 30.5, "children_rate": 13.9},
    {"year": 2010, "rate": 35.7, "children_rate": 16.9},
    {"year": 2020, "rate": 41.9, "children_rate": 19.7},
    {"year": 2024, "rate": 43.0, "children_rate": 21.0}
  ]
}
```

##### Step 3.3: News Scraper (`src/research/news_scraper.py`)

```python
# src/research/news_scraper.py
"""
Fetches trending food-safety and nutrition news from multiple sources.
"""
import feedparser
import requests
from datetime import datetime, timedelta
from src.config import PROVIDERS  # No NEWS_API_KEY needed — using RSS feeds

# Google News RSS search queries — no API key needed
GOOGLE_NEWS_QUERIES = [
    "food safety recall",
    "FDA food regulation",
    "ultra processed food health",
    "food additive banned",
    "obesity epidemic USA",
    "toxic food ingredients",
]

def fetch_trending_news(days: int = 7, max_results: int = 20) -> list[dict]:
    """
    Fetch recent food-safety news from available sources.
    Uses Google News RSS (free, no API key needed) as the primary source.
    All your LLM API keys are text-generation models, so news fetching
    uses RSS feeds. Grok is used later for *analyzing* the news context.
    """
    articles = []

    # Always use Google News RSS (free, no API key needed)
    articles.extend(_fetch_from_google_rss(max_results))

    # Deduplicate by title similarity, sort by date
    articles = _deduplicate(articles)
    articles.sort(key=lambda a: a.get("date", ""), reverse=True)

    return articles[:max_results]


def _fetch_from_google_rss(max_per_query: int = 5) -> list[dict]:
    """Fetch from Google News RSS feeds (free, no API key)."""
    articles = []
    for query in GOOGLE_NEWS_QUERIES:
        feed_url = (
            f"https://news.google.com/rss/search?q={query.replace(' ', '+')}"
            f"&hl=en-US&gl=US&ceid=US:en"
        )
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:max_per_query]:
            articles.append({
                "title": entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "source": entry.get("source", {}).get("title", "Google News"),
                "url": entry.get("link", ""),
                "date": entry.get("published", "")[:10] if entry.get("published") else "",
                "origin": "google_rss",
            })
    return articles


def _deduplicate(articles: list[dict]) -> list[dict]:
    """Remove near-duplicate articles based on title similarity."""
    seen_titles = set()
    unique = []
    for a in articles:
        # Simple dedup: lowercase first 50 chars of title
        key = a["title"].lower()[:50]
        if key not in seen_titles:
            seen_titles.add(key)
            unique.append(a)
    return unique


def format_for_prompt(articles: list[dict], count: int = 5) -> str:
    """Format news articles into an LLM-injectable string."""
    lines = ["TRENDING FOOD SAFETY NEWS:"]
    for a in articles[:count]:
        lines.append(
            f"  • [{a['date']}] {a['title']} (Source: {a['source']})\n"
            f"    Summary: {a['summary']}"
        )
    return "\n".join(lines)
```

**How it works**:
1. Tries NewsAPI first (higher quality, requires API key).
2. Always supplements with Google News RSS (free, no key needed).
3. Deduplicates by title similarity.
4. Returns structured article dicts and can format them for prompt injection.

---

#### PHASE 4 — Orchestration Scripts

##### Step 4.1: Repertoire Generator (`scripts/generate_repertoire.py`)

This is the main entry point for generating a batch of content ideas and bilingual screenplays.

```python
# scripts/generate_repertoire.py
"""
Generate a batch of content ideas and bilingual screenplays.

Usage:
    python scripts/generate_repertoire.py --count 10 --pillar all --lang both
"""
import sys
import click
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generators.idea_generator import generate_ideas
from src.generators.screenplay_writer import write_screenplay
from src.research.food_database import (
    load_food_facts, get_random_comparisons, get_random_deep_dives, format_for_prompt as format_food,
)
from src.research.regulation_research import (
    get_banned_additives, get_timeline_events, get_obesity_stats, format_for_prompt as format_reg,
)

@click.command()
@click.option("--count", default=5, help="Number of ideas to generate")
@click.option("--pillar", default="all",
              type=click.Choice(["all", "comparison", "deep-dive", "regulation", "trending"]))
@click.option("--screenplays/--no-screenplays", default=True,
              help="Also generate full screenplays for each idea")
def main(count, pillar, screenplays):
    """Generate a repertoire of content ideas and bilingual screenplays."""
    click.echo(f"\n🎬 Generating {count} ideas (pillar: {pillar})...\n")

    # Gather research context
    food_context = format_food(get_random_comparisons(5) + get_random_deep_dives(5))
    reg_context = format_reg(
        additives=get_banned_additives(5),
        events=get_timeline_events(5),
        stats=get_obesity_stats(),
    )

    # Generate ideas
    ideas = generate_ideas(
        count=count,
        pillar=pillar,
        food_context=food_context,
        regulation_context=reg_context,
    )

    click.echo(f"✅ Generated {len(ideas)} ideas\n")
    for i, idea in enumerate(ideas, 1):
        title = idea.get("title_en", idea.get("title", "Untitled"))
        click.echo(f"  {i}. [{idea.get('pillar', '?')}] {title}")

    # Generate screenplays if requested
    if screenplays:
        click.echo(f"\n📝 Generating bilingual screenplays (EN + ES)...\n")
        for i, idea in enumerate(ideas, 1):
            title = idea.get("title_en", idea.get("title", "Untitled"))
            click.echo(f"  Writing screenplay {i}/{len(ideas)}: {title}...")
            result = write_screenplay(
                idea=idea,
                food_context=food_context,
                regulation_context=reg_context,
            )
            click.echo(f"    → EN: {result['en_path']}")
            click.echo(f"    → ES: {result['es_path']}")

    click.echo(f"\n🎉 Done! Check data/generated/ for output.\n")

if __name__ == "__main__":
    main()
```

##### Step 4.2: Trending News Generator (`scripts/generate_from_trending.py`)

```python
# scripts/generate_from_trending.py
"""
Fetch trending food-safety news and generate reactive content.

Usage:
    python scripts/generate_from_trending.py --count 3 --days 7
"""
import sys
import click
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generators.idea_generator import generate_ideas
from src.generators.screenplay_writer import write_screenplay
from src.research.news_scraper import fetch_trending_news, format_for_prompt as format_news
from src.research.regulation_research import (
    get_banned_additives, get_timeline_events, format_for_prompt as format_reg,
)

@click.command()
@click.option("--count", default=3, help="Number of ideas to generate")
@click.option("--days", default=7, help="How many days back to search for news")
@click.option("--screenplays/--no-screenplays", default=True)
def main(count, days, screenplays):
    """Generate content ideas from trending food-safety news."""

    # Fetch trending news
    click.echo(f"\n📰 Fetching trending food-safety news (last {days} days)...\n")
    articles = fetch_trending_news(days=days)
    click.echo(f"  Found {len(articles)} articles")

    if not articles:
        click.echo("  ⚠️  No trending news found. Try increasing --days.")
        return

    # Show top headlines
    for a in articles[:5]:
        click.echo(f"  • [{a['date']}] {a['title']}")

    # Build context
    news_context = format_news(articles, count=8)
    reg_context = format_reg(
        additives=get_banned_additives(3),
        events=get_timeline_events(3),
    )

    # Generate ideas focused on trending pillar
    # Uses GROK as the LLM provider — best for trending/current events awareness
    click.echo(f"\n🎬 Generating {count} trending-reactive ideas (via Grok)...\n")
    ideas = generate_ideas(
        count=count,
        pillar="trending",
        news_context=news_context,
        regulation_context=reg_context,
        provider="grok",  # Grok has real-time X/Twitter awareness
    )

    for i, idea in enumerate(ideas, 1):
        title = idea.get("title_en", idea.get("title", "Untitled"))
        click.echo(f"  {i}. {title}")

    if screenplays:
        click.echo(f"\n📝 Generating bilingual screenplays...\n")
        for i, idea in enumerate(ideas, 1):
            title = idea.get("title_en", idea.get("title", "Untitled"))
            click.echo(f"  Writing {i}/{len(ideas)}: {title}...")
            result = write_screenplay(idea=idea, regulation_context=reg_context)
            click.echo(f"    → EN: {result['en_path']}")
            click.echo(f"    → ES: {result['es_path']}")

    click.echo(f"\n🎉 Done!\n")

if __name__ == "__main__":
    main()
```

---

#### PHASE 5 — Shooting Guide Animation Generator (Independent)

##### Step 5.1: Animation Generator (`src/generators/animation_generator.py`)

This module parses a screenplay and produces a visual storyboard/shooting-guide animation.
It uses a **tiered approach**: Gemini Veo (AI video) → Gemini Imagen/DALL-E (storyboard images) → Manim (programmatic fallback).

```python
# src/generators/animation_generator.py
"""
Generates shooting guide / storyboard animations from screenplays.

TIERED APPROACH:
  1. Gemini Veo (veo-3)  → AI-generated video clips per scene (best quality)
  2. Gemini Imagen / DALL-E 3 → AI-generated storyboard frames stitched into video
  3. Manim → Programmatic stick-figure animation (offline fallback)

This is a PERSONAL reference for the creator — NOT published content.
"""
import json
import time
from pathlib import Path
from google import genai
from google.genai import types as genai_types

from src.llm_client import call_llm
from src.persona import SYSTEM_PROMPT_ANIMATION_GUIDE
from src.config import (
    ANIMATIONS_DIR, PROVIDERS, GEMINI_KEY, OPENAI_KEY, DEFAULT_PROVIDERS,
)


# ── Step 1: Parse screenplay into shot-by-shot directing data ──────

def parse_screenplay_for_animation(screenplay_path: str) -> list[dict]:
    """
    Read a screenplay file and use the LLM to extract structured
    shot-by-shot blocking/directing instructions.

    Returns a list of scene dicts with fields:
      time_code, section, duration_seconds, camera, body_position,
      facial_expression, hand_action, props, text_overlay, movement,
      transition_to_next, veo_prompt, imagen_prompt
    """
    screenplay_text = Path(screenplay_path).read_text(encoding="utf-8")

    user_prompt = f"""Analyze this screenplay and extract shot-by-shot DIRECTING
instructions for the creator. For each time block, describe EXACTLY how she
should position herself, what expression to make, where to look, what to hold,
and where the camera should be.

ALSO for each scene, write:
- "veo_prompt": A detailed text-to-video prompt (for Veo) describing a young
  Latina woman performing the exact action in a home kitchen setting.
  Be specific about body position, camera angle, lighting, and movement.
- "imagen_prompt": A text-to-image prompt (for Imagen/DALL-E) depicting the
  key moment of this shot as a storyboard frame.

SCREENPLAY:
{screenplay_text}

Return as a JSON object with a "scenes" array of scene objects.
"""

    response = call_llm(
        system_prompt=SYSTEM_PROMPT_ANIMATION_GUIDE,
        user_prompt=user_prompt,
        task="idea_generation",  # uses Gemini (fast, structured output)
    )

    data = json.loads(response)
    if isinstance(data, dict) and "scenes" in data:
        return data["scenes"]
    if isinstance(data, list):
        return data
    return []


# ── Step 2A: Gemini Veo — AI Video Generation (Best Quality) ──────

def _generate_via_veo(scenes: list[dict], output_dir: Path) -> list[Path]:
    """
    Generate a short video clip per scene using Gemini Veo.
    Returns list of video file paths.
    """
    client = genai.Client(api_key=GEMINI_KEY)
    video_model = PROVIDERS["gemini"]["models"]["video"]  # "veo-3"
    clips = []

    for i, scene in enumerate(scenes):
        prompt = scene.get("veo_prompt", "")
        if not prompt:
            prompt = (
                f"A young Latina woman in a home kitchen. "
                f"Camera: {scene.get('camera', 'medium shot')}. "
                f"She is {scene.get('body_position', 'standing behind counter')}. "
                f"Expression: {scene.get('facial_expression', 'smiling')}. "
                f"Action: {scene.get('hand_action', '')}. "
                f"Duration: {scene.get('duration_seconds', 3)} seconds. "
                f"Storyboard / shooting guide reference style."
            )

        # Generate video with Veo
        operation = client.models.generate_videos(
            model=video_model,
            prompt=prompt,
            config=genai_types.GenerateVideosConfig(
                number_of_videos=1,
                duration_seconds=min(scene.get("duration_seconds", 5), 8),
                person_generation="allow_all",
            ),
        )

        # Poll until video is ready
        while not operation.done:
            time.sleep(10)
            operation = client.operations.get(operation)

        # Save the video clip
        clip_path = output_dir / f"scene_{i+1:02d}_{scene.get('section', 'SCENE')}.mp4"
        for vid in operation.result.generated_videos:
            video_data = client.files.download(file=vid.video)
            clip_path.write_bytes(video_data)
            clips.append(clip_path)
            break  # Take first result

    return clips


# ── Step 2B: Gemini Imagen — Storyboard Frame Images ─────────────

def _generate_via_imagen(scenes: list[dict], output_dir: Path) -> list[Path]:
    """
    Generate one storyboard image per scene using Gemini Imagen.
    Returns list of image file paths.
    """
    client = genai.Client(api_key=GEMINI_KEY)
    image_model = PROVIDERS["gemini"]["models"]["image"]  # "imagen-3"
    frames = []

    for i, scene in enumerate(scenes):
        prompt = scene.get("imagen_prompt", "")
        if not prompt:
            prompt = (
                f"Storyboard frame: A young Latina woman in home kitchen. "
                f"Camera angle: {scene.get('camera', 'medium shot')}. "
                f"Position: {scene.get('body_position', '')}. "
                f"Expression: {scene.get('facial_expression', '')}. "
                f"Props: {', '.join(p['name'] for p in scene.get('props', []))}. "
                f"Annotated storyboard style with shot labels."
            )

        response = client.models.generate_images(
            model=image_model,
            prompt=prompt,
            config=genai_types.GenerateImagesConfig(
                number_of_images=1,
            ),
        )

        frame_path = output_dir / f"frame_{i+1:02d}_{scene.get('section', 'SCENE')}.png"
        for img in response.generated_images:
            img.image.save(str(frame_path))
            frames.append(frame_path)
            break

    return frames


# ── Step 2C: DALL-E 3 — Alternative Storyboard Frames ────────────

def _generate_via_dalle(scenes: list[dict], output_dir: Path) -> list[Path]:
    """
    Generate storyboard frames using OpenAI DALL-E 3 as an alternative.
    """
    from openai import OpenAI
    import requests as req

    client = OpenAI(api_key=OPENAI_KEY)
    frames = []

    for i, scene in enumerate(scenes):
        prompt = scene.get("imagen_prompt", "")  # Reuse same prompt structure
        if not prompt:
            prompt = (
                f"Storyboard frame for a cooking video: young Latina woman "
                f"in home kitchen, {scene.get('camera', 'medium shot')}, "
                f"{scene.get('body_position', '')}, {scene.get('facial_expression', '')}."
            )

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            n=1,
        )

        frame_path = output_dir / f"frame_{i+1:02d}_{scene.get('section', 'SCENE')}.png"
        img_url = response.data[0].url
        img_data = req.get(img_url, timeout=30).content
        frame_path.write_bytes(img_data)
        frames.append(frame_path)

    return frames


# ── Step 3: Stitch frames into a video with annotations ──────────

def _stitch_frames_to_video(
    frames: list[Path], scenes: list[dict], output_path: Path
) -> str:
    """Combine storyboard frame images into a video using MoviePy."""
    from moviepy.editor import (
        ImageClip, concatenate_videoclips, TextClip, CompositeVideoClip,
    )

    clips = []
    for frame, scene in zip(frames, scenes):
        duration = scene.get("duration_seconds", 3)

        # Create image clip
        img_clip = ImageClip(str(frame)).set_duration(duration)

        # Add text overlay with scene info
        label = (
            f"[{scene.get('time_code', '')}] {scene.get('section', '')}\n"
            f"Camera: {scene.get('camera', '')}\n"
            f"Action: {scene.get('movement', 'Hold')}"
        )
        txt_clip = (
            TextClip(label, fontsize=20, color="yellow", bg_color="black",
                     font="Arial", method="caption", size=(400, None))
            .set_position(("left", "bottom"))
            .set_duration(duration)
        )

        composite = CompositeVideoClip([img_clip, txt_clip])
        clips.append(composite)

    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(str(output_path), fps=24)
    return str(output_path)


# ── Step 4: Manim Fallback (offline, no API needed) ──────────────
# (Same Manim ShootingGuideScene class as previously defined —
#  stick-figure animation with camera overlays and timing markers.
#  Omitted here for brevity; see earlier Manim code in this plan.)


# ── Main Entry Point ─────────────────────────────────────────────

def generate_shooting_guide(
    screenplay_path: str,
    output_name: str = None,
    mode: str = "auto",
) -> str:
    """
    Main entry point: parse a screenplay → generate shooting guide animation.

    Args:
        screenplay_path: Path to the screenplay .md file.
        output_name: Optional output filename (without extension).
        mode: Generation mode:
            "auto"       — Try Veo → Imagen → Manim (in order)
            "veo"        — Gemini Veo video only
            "storyboard" — Gemini Imagen or DALL-E storyboard frames
            "manim"      — Programmatic Manim animation (offline)

    Returns:
        Path to the generated MP4 file.
    """
    scenes_data = parse_screenplay_for_animation(screenplay_path)
    if not scenes_data:
        raise ValueError("Could not extract scene data from screenplay.")

    if not output_name:
        output_name = Path(screenplay_path).stem + "_shooting_guide"

    output_path = ANIMATIONS_DIR / f"{output_name}.mp4"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    temp_dir = ANIMATIONS_DIR / f"_temp_{output_name}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    if mode == "auto":
        # Tier 1: Try Gemini Veo
        try:
            clips = _generate_via_veo(scenes_data, temp_dir)
            # Stitch Veo clips together
            from moviepy.editor import VideoFileClip, concatenate_videoclips
            vclips = [VideoFileClip(str(c)) for c in clips]
            final = concatenate_videoclips(vclips)
            final.write_videofile(str(output_path), fps=24)
            return str(output_path)
        except Exception as e:
            print(f"⚠️  Veo generation failed ({e}), trying storyboard mode...")

        # Tier 2: Try Imagen storyboard
        try:
            frames = _generate_via_imagen(scenes_data, temp_dir)
            _stitch_frames_to_video(frames, scenes_data, output_path)
            return str(output_path)
        except Exception as e:
            print(f"⚠️  Imagen generation failed ({e}), trying DALL-E...")

        # Tier 2b: Try DALL-E storyboard
        try:
            frames = _generate_via_dalle(scenes_data, temp_dir)
            _stitch_frames_to_video(frames, scenes_data, output_path)
            return str(output_path)
        except Exception as e:
            print(f"⚠️  DALL-E generation failed ({e}), falling back to Manim...")

        # Tier 3: Manim fallback
        # (Manim ShootingGuideScene rendering — programmatic, no API needed)

    elif mode == "veo":
        clips = _generate_via_veo(scenes_data, temp_dir)
        from moviepy.editor import VideoFileClip, concatenate_videoclips
        vclips = [VideoFileClip(str(c)) for c in clips]
        final = concatenate_videoclips(vclips)
        final.write_videofile(str(output_path), fps=24)

    elif mode == "storyboard":
        try:
            frames = _generate_via_imagen(scenes_data, temp_dir)
        except Exception:
            frames = _generate_via_dalle(scenes_data, temp_dir)
        _stitch_frames_to_video(frames, scenes_data, output_path)

    elif mode == "manim":
        pass  # Manim fallback rendering

    return str(output_path)
```

##### Step 5.2: Standalone Animation Script (`scripts/generate_animation.py`)

```python
# scripts/generate_animation.py
"""
Standalone script to generate shooting guide animations from screenplays.

Usage:
    python scripts/generate_animation.py --screenplay data/generated/screenplays/en/my_video.md
    python scripts/generate_animation.py --screenplay path/to/screenplay.md --output my_guide
"""
import sys
import click
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generators.animation_generator import generate_shooting_guide

@click.command()
@click.option("--screenplay", required=True, type=click.Path(exists=True),
              help="Path to the screenplay .md file")
@click.option("--output", default=None, help="Output filename (without extension)")
@click.option("--mode", default="auto",
              type=click.Choice(["auto", "veo", "storyboard", "manim"]),
              help="Generation mode: auto (try best→fallback), veo (Gemini video), "
                   "storyboard (Imagen/DALL-E frames), manim (offline stick-figure)")
def main(screenplay, output, mode):
    """Generate a shooting guide animation from a screenplay."""
    click.echo(f"\n🎬 Generating shooting guide animation (mode: {mode})...")
    click.echo(f"  Screenplay: {screenplay}")

    result_path = generate_shooting_guide(
        screenplay_path=screenplay,
        output_name=output,
        mode=mode,
    )

    click.echo(f"\n✅ Shooting guide saved to: {result_path}")
    click.echo("  This is your personal director's reference — not for publishing.\n")

if __name__ == "__main__":
    main()
```

---

#### PHASE 6 — Output Formatting & Templates

##### Step 6.1: Jinja2 Templates (`templates/`)

Create reusable Markdown templates for formatted screenplay output.

**`templates/screenplay_en.md.j2`** — English screenplay template:

```jinja2
# 🎬 {{ title }}

**Pillar**: {{ pillar }}
**Duration**: {{ duration }} seconds
**Platform**: {{ platform }}

---

## Props Needed
{% for prop in props %}
- {{ prop }}
{% endfor %}

## Shooting Notes
{{ shooting_notes }}

---

{% for scene in scenes %}
### [{{ scene.time_code }}] {{ scene.section }}

**VISUAL**: {{ scene.visual }}

**VOICEOVER** _({{ scene.tone }})_:
> {{ scene.dialogue }}

{% if scene.on_screen_text %}
**ON-SCREEN TEXT**: {{ scene.on_screen_text }}
{% endif %}

{% if scene.sound %}
**SOUND/MUSIC**: {{ scene.sound }}
{% endif %}

---
{% endfor %}

## Hashtags
{{ hashtags }}

## Music
{{ music }}
```

**`templates/screenplay_es.md.j2`** — Spanish version (same structure, Spanish labels).

##### Step 6.2: Formatter (`src/output/formatter.py`)

```python
# src/output/formatter.py
"""
Formats generated content into polished output using Jinja2 templates.
"""
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from src.config import TEMPLATES_DIR

env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

def format_screenplay(screenplay_data: dict, language: str = "en") -> str:
    """Render a screenplay dict through the Jinja2 template."""
    template_name = f"screenplay_{language}.md.j2"
    template = env.get_template(template_name)
    return template.render(**screenplay_data)
```

---

#### PHASE 7 — Periodic Scheduling & Automation

##### Step 7.1: Scheduler (`src/scheduler/periodic_runner.py`)

```python
# src/scheduler/periodic_runner.py
"""
Runs content generation on a schedule.
Can be run as a long-lived process or triggered via system cron.
"""
import schedule
import time
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"


def run_trending():
    """Run the trending news content generator."""
    subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "generate_from_trending.py"),
         "--count", "3", "--days", "3"],
        check=True,
    )


def run_weekly_repertoire():
    """Run the weekly repertoire generator."""
    subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "generate_repertoire.py"),
         "--count", "5", "--pillar", "all"],
        check=True,
    )


def start_scheduler():
    """Start the periodic scheduler (blocking)."""
    schedule.every().day.at("08:00").do(run_trending)
    schedule.every().monday.at("09:00").do(run_weekly_repertoire)

    print("📅 Scheduler started.")
    print("  • Daily 8:00 AM — Trending news content generation")
    print("  • Monday 9:00 AM — Weekly repertoire refresh")
    print("  Press Ctrl+C to stop.\n")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    start_scheduler()
```

**Alternative: system cron** (for production):
```bash
# crontab -e
# Daily at 8 AM — trending content
0 8 * * * cd /home/jude/ai_influener && venv/bin/python scripts/generate_from_trending.py --count 3

# Weekly Monday 9 AM — repertoire refresh
0 9 * * 1 cd /home/jude/ai_influener && venv/bin/python scripts/generate_repertoire.py --count 5
```

---

#### PHASE 8 — Testing & Validation

##### Step 8.1: Unit Tests (`tests/`)

```
tests/
├── __init__.py
├── test_config.py              # Test .env loading and path resolution
├── test_idea_generator.py      # Test idea generation (mock LLM)
├── test_screenplay_writer.py   # Test bilingual splitting, slugify, file saving
├── test_news_scraper.py        # Test RSS parsing, deduplication
├── test_food_database.py       # Test data loading, random selection
├── test_regulation_research.py # Test data loading, formatting
└── test_animation_generator.py # Test screenplay parsing, scene extraction
```

Key testing strategies:
- **Mock LLM calls** in unit tests using `unittest.mock.patch` on `call_llm()`.
- **Test bilingual splitting** with various LLM output formats (ensure both EN and ES are extracted).
- **Test news deduplication** with sample article data.
- **Integration tests**: Run `generate_repertoire.py --count 1` with a real API key to verify end-to-end.

##### Step 8.2: Manual Validation Checklist

After each generation run, verify:
- [ ] Ideas JSON is valid and contains all required fields
- [ ] English screenplay is natural, on-brand, and follows time-code structure
- [ ] Spanish screenplay is naturally written (not machine-translated), culturally appropriate
- [ ] Hashtags include both English and Spanish versions
- [ ] Shooting guide animation (when generated) matches the screenplay's shot sequence
- [ ] Props lists are realistic and achievable in a home kitchen setup
- [ ] Educational claims are factually grounded in the injected research data

---

#### Implementation Order & Dependencies

```
Step 1.1  Project scaffolding ──────────────────────────────────┐
Step 1.2  requirements.txt                                      │
Step 1.3  config.py                                             │
Step 1.4  persona.py                                            │
Step 1.5  llm_client.py ───────────────────────────────────────┤
                                                                │
Step 3.1  food_database.py + food_facts.json ──┐                │
Step 3.2  regulation_research.py + data ───────┤ (parallel)     │
Step 3.3  news_scraper.py ─────────────────────┘                │
                                                                │
Step 2.1  idea_generator.py ←── depends on 1.5, persona ───────┤
Step 2.2  screenplay_writer.py ←── depends on 1.5, persona ────┤
                                                                │
Step 4.1  generate_repertoire.py ←── depends on 2.1, 2.2, 3.x │
Step 4.2  generate_from_trending.py ←── depends on 2.1, 3.3    │
                                                                │
Step 5.1  animation_generator.py ←── depends on 1.5 (standalone)│
Step 5.2  generate_animation.py ←── depends on 5.1             │
                                                                │
Step 6.1  templates/ ──────────────────────────────────────────│
Step 6.2  formatter.py                                          │
                                                                │
Step 7.1  periodic_runner.py ←── depends on 4.1, 4.2           │
Step 8.x  tests ←── after each module is done                  │
```

**Parallelizable work**: Steps 3.1, 3.2, and 3.3 (research modules) can be built in parallel since they have no dependencies on each other. Step 5.x (animation) is fully independent and can be built any time after Step 1.5.

---

#### Quick-Start: First Working Pipeline

To get a working demo as fast as possible, build in this minimal order:

1. **config.py** + **persona.py** + **llm_client.py** (10 min setup)
2. **idea_generator.py** (first LLM-powered output)
3. **screenplay_writer.py** (first bilingual screenplays)
4. **generate_repertoire.py** (first runnable script)

After step 4, you can run:
```bash
source venv/bin/activate
python scripts/generate_repertoire.py --count 3
```
...and get 3 content ideas with full bilingual screenplays saved to disk.

Everything else (news scraper, animation, scheduling, templates) layers on top of this core.

---

### Example Generated Screenplay

```
═══════════════════════════════════════════════════════════════
                        🇺🇸 ENGLISH VERSION
═══════════════════════════════════════════════════════════════

TITLE: "This is BANNED in 30 Countries But America Says It's Fine 🤮"
PILLAR: US Regulation Exposé + Food Comparison
DURATION: 45 seconds
PLATFORM: TikTok

[0-2s] HOOK
(Close-up of brightly colored cereal being poured)
VOICEOVER (shocked tone): "This cereal is ILLEGAL in Europe."

[2-8s] SETUP
(Cut to host in kitchen, holding two cereal boxes)
VOICEOVER: "Same brand. Same name. But look at the ingredients..."
(Side-by-side ingredient labels zoom in)
ON-SCREEN TEXT: "US version: Red 40, Yellow 5, BHT"
ON-SCREEN TEXT: "EU version: Beetroot extract, Paprika extract"

[8-35s] CORE CONTENT
(Host in kitchen, animated overlay showing additive effects)
VOICEOVER: "Red 40 is linked to hyperactivity in children.
The EU made them use natural colors instead.
But in America? The FDA said 'it's fine.'
Meanwhile, childhood obesity went from 5% in 1980 to over 20% today."
(Animation: obesity rate timeline graph appears)

[35-45s] CTA
(Host eating colorful salad, smiling)
VOICEOVER: "Make your own colorful breakfast instead — recipe in part 2!"
ON-SCREEN TEXT: "Follow for more food truths 🔥"

HASHTAGS: #foodsafety #whatieatinaday #healthyfood #banned #fdalies
MUSIC: Trending dramatic reveal sound → upbeat cooking beat

═══════════════════════════════════════════════════════════════
                        🇪🇸 VERSIÓN EN ESPAÑOL
═══════════════════════════════════════════════════════════════

TÍTULO: "Esto está PROHIBIDO en 30 Países Pero en Estados Unidos Dicen Que Está Bien 🤮"
PILAR: Exposé de Regulaciones de EE.UU. + Comparación de Alimentos
DURACIÓN: 45 segundos
PLATAFORMA: TikTok

[0-2s] GANCHO
(Primer plano de cereal de colores brillantes siendo servido)
VOZ EN OFF (tono de sorpresa): "Este cereal es ILEGAL en Europa."

[2-8s] CONTEXTO
(Corte a la presentadora en la cocina, sosteniendo dos cajas de cereal)
VOZ EN OFF: "Misma marca. Mismo nombre. Pero mira los ingredientes..."
(Zoom a las etiquetas de ingredientes lado a lado)
TEXTO EN PANTALLA: "Versión EE.UU.: Rojo 40, Amarillo 5, BHT"
TEXTO EN PANTALLA: "Versión UE: Extracto de remolacha, Extracto de pimentón"

[8-35s] CONTENIDO PRINCIPAL
(Presentadora en la cocina, superposición animada mostrando efectos de los aditivos)
VOZ EN OFF: "El Rojo 40 está vinculado a la hiperactividad en niños.
La UE los obligó a usar colorantes naturales.
Pero en Estados Unidos, la FDA dijo 'está bien.'
Mientras tanto, la obesidad infantil pasó del 5% en 1980 a más del 20% hoy."
(Animación: gráfica de línea de tiempo de tasas de obesidad)

[35-45s] LLAMADA A LA ACCIÓN
(Presentadora comiendo una ensalada colorida, sonriendo)
VOZ EN OFF: "¡Mejor prepárate un desayuno colorido tú misma — receta en la parte 2!"
TEXTO EN PANTALLA: "Sígueme para más verdades sobre la comida 🔥"

HASHTAGS: #seguridadalimentaria #comidasaludable #prohibido #fda #alimentossanos #comidatoxica
MÚSICA: Sonido dramático de revelación en tendencia → ritmo alegre de cocina
```

---

### Key Design Decisions

1. **LLM as core engine**: All creative generation (ideas, screenplays, hooks) flows through the LLM with carefully crafted system prompts that encode the persona and brand guidelines.
2. **Separation of concerns**: Research, generation, and animation are independent modules. The animation script runs standalone as requested.
3. **Bilingual by default**: Every screenplay is generated in both English and Spanish simultaneously, maximizing audience reach and letting the creator choose language per video (or mix both for code-switching appeal).
4. **Animations = shooting guides**: Demonstration animations are personal director's references — they show the creator how to position, act, and frame shots, not published viewer-facing content.
5. **Data-backed education**: Pre-curated regulation facts and food data ground the LLM output in verified information, reducing hallucination risk for educational claims.
6. **Trending-first content**: The news scraper ensures content stays timely and can ride algorithmic waves from viral food-safety stories.
7. **Batch + periodic**: Initial repertoire generation seeds the content library; periodic runs keep it fresh without manual intervention.

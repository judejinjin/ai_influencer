# Content Pipeline Workflow

## Overview

AI-powered bilingual (EN/ES) content pipeline for a TikTok healthy-food influencer.
Generates ideas → screenplays → shooting-guide animations with voiceover.

---

## Step 1: Idea Generation

**Script:** `scripts/generate_repertoire.py`
**Model:** gemini-2.5-flash (~$0.01/idea)
**Fallback:** gpt-4o → grok-3 → openrouter (free)

Reads seed data (`food_facts.json`, `daily_staples.json`, `regulation_timeline.json`) and generates content ideas across 5 pillars:

1. **Comparisons** — healthy vs ultra-processed food
2. **Deep-dives** — single ingredient breakdowns
3. **Regulation (additives)** — banned substances still in US food
4. **Regulation (timeline)** — policy changes over time
5. **Daily staples** — everyday foods analyzed

Coverage tracked in `data/generated/coverage_log.json` — re-runs skip already-covered items.

```bash
# Cover all seed data
python scripts/generate_repertoire.py --exhaust
```

**Output:** `data/generated/ideas/ideas_YYYYMMDD_HHMMSS.json`

---

## Step 2: Screenplay Writing

**Script:** `scripts/generate_repertoire.py` (runs automatically after ideas unless `--no-screenplays`)
**Model:** claude-sonnet-4-20250514 (~$0.01/screenplay)
**Templates:** `templates/screenplay_en.md.j2`, `templates/screenplay_es.md.j2`

Each idea becomes a bilingual pair of screenplays (EN + ES) with:
- Scene breakdowns with timecodes
- Camera directions, body positions, facial expressions
- Voiceover narration text
- Props and hand actions

**Output:**
- `data/generated/screenplays/en/*.md`
- `data/generated/screenplays/es/*.md`

---

## Step 3: Trending News (Optional)

**Script:** `scripts/generate_from_trending.py`
**Model:** grok-3 (real-time news awareness)

Fetches recent food-safety news and generates reactive content ideas + screenplays.

```bash
python scripts/generate_from_trending.py --count 3 --days 7
```

---

## Step 4: Animation Generation

**Script:** `scripts/generate_animation.py`

### 4a. Scene Parsing
**Model:** gemini-2.5-flash (max_tokens=16000, ~$0.01/parse)

LLM extracts structured scene data (camera, body position, voiceover text, duration) from screenplay markdown. 3-level JSON defense: direct parse → escape fix → LLM repair.

### 4b. Image Generation
**With headshot** (`--headshot`): gemini-2.5-flash-image / Nano Banana ($0.039/image)
- Headshot resized to ≤512px JPEG, cached in memory
- Face appears consistently across all storyboard frames

**Without headshot**: imagen-4.0-fast-generate-001 ($0.02/image)

**Fallback**: dall-e-3 ($0.04/image) → Manim stick figures (free, offline)

### 4c. Silent Base Video
Images stitched into a silent MP4 using moviepy (local, free). Scene durations from screenplay. Saved as temp file.

### 4d. Voice Overlay
**EN voice:** en-US-AriaNeural (edge-tts, free) — young, confident female
**ES voice:** es-MX-DaliaNeural (edge-tts, free) — female Mexican Spanish
**Pitch:** +10Hz | **Rate:** +0%

Each language gets its own MP4 from the silent base:
1. Silent base video generated (images only)
2. EN voiceover overlaid → `*_shooting_guide_en.mp4`
3. ES voiceover overlaid → `*_shooting_guide_es.mp4`
4. Silent base deleted

If audio is longer than a scene, the last frame freezes to accommodate.

```bash
# Generate all EN+ES animations with headshot
python scripts/generate_animation.py --all --lang both --headshot data/wm_with_glasses_512.jpg
```

**Output:**
- `data/generated/animations/*_shooting_guide_en.mp4`
- `data/generated/animations/*_shooting_guide_es.mp4`

---

## Pipeline Diagram

```
seed data ─────→ [generate_repertoire.py] ─→ ideas (JSON)
                        │                        │
                        └────────────────────→ screenplays (EN + ES .md)
                                                    │
trending news ─→ [generate_from_trending.py] ──────→│
                                                    │
                                                    ▼
                                        [generate_animation.py]
                                                    │
                                    ┌───────────────┼───────────────┐
                                    ▼               ▼               ▼
                              scene parsing   image generation   TTS generation
                              (gemini-2.5)    (imagen-4/nano)    (edge-tts)
                                    │               │               │
                                    │               ▼               │
                                    │        silent base .mp4       │
                                    │          (moviepy)            │
                                    │               │               │
                                    │       ┌───────┴───────┐      │
                                    │       ▼               ▼      │
                                    │   EN voice        ES voice   │
                                    │   overlay         overlay    │
                                    │       │               │      │
                                    ▼       ▼               ▼      ▼
                                  *_en.mp4            *_es.mp4
```

---

## Cost Estimate (122 ideas, EN+ES)

| Mode | Images | LLM | TTS | Total |
|------|--------|-----|-----|-------|
| Without headshot | ~$20 (Imagen 4) | ~$3 | $0 | **~$23** |
| With headshot | ~$38 (Nano Banana) | ~$3 | $0 | **~$41** |

---

## Key Files

| File | Purpose |
|------|---------|
| `src/config.py` | Models, API keys, directories, provider settings |
| `src/llm_client.py` | Multi-provider LLM client with fallback + circuit breaker |
| `src/persona.py` | System prompts for the influencer persona |
| `src/generators/animation_generator.py` | Full animation pipeline (parse → images → TTS → stitch) |
| `src/generators/idea_generator.py` | Content idea generation |
| `src/generators/screenplay_writer.py` | Bilingual screenplay generation |
| `scripts/generate_animation.py` | CLI for animation batch processing |
| `scripts/generate_repertoire.py` | CLI for idea + screenplay generation |
| `scripts/generate_from_trending.py` | CLI for trending news content |
| `scripts/resize_headshot.py` | Headshot preprocessing utility |

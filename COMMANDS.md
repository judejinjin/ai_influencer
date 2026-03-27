# Generation Commands Reference

## 1. Content Ideas & Screenplays — `generate_repertoire.py`

Generate content ideas from seed data and expand them into bilingual (EN+ES) screenplays.

### Flags

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--count` | int | 5 | Number of ideas to generate (ignored with `--exhaust`) |
| `--pillar` | `all\|comparison\|deep-dive\|regulation\|trending` | `all` | Content pillar to focus on |
| `--screenplays` / `--no-screenplays` | bool | True | Also generate full screenplays for each idea |
| `--exhaust` | flag | False | Systematically cover ALL seed data items (ignores `--count` and `--pillar`) |
| `--ideas-per-item` | int | 2 | Number of ideas per seed data item in `--exhaust` mode |
| `--reset-coverage` | flag | False | Clear the coverage log and start fresh |

### Exhaust Mode Pillars (processed in order)

1. **Comparisons** — one batch per food comparison from `food_facts.json`
2. **Deep-dives** — one batch per ingredient
3. **Regulation (additives)** — one batch per banned additive
4. **Regulation (timeline)** — one batch per timeline event
5. **Daily staples** — one batch per staple from `daily_staples.json`

Coverage is tracked in `data/generated/coverage_log.json` — re-runs skip already-covered items.

### Examples

```bash
# Quick test: 5 ideas + screenplays
python scripts/generate_repertoire.py --count 5 --pillar comparison

# Cover ALL seed data (ideas + screenplays)
python scripts/generate_repertoire.py --exhaust

# Ideas only, no screenplays
python scripts/generate_repertoire.py --exhaust --no-screenplays

# Wipe coverage log and regenerate everything from scratch
python scripts/generate_repertoire.py --reset-coverage --exhaust

# 1 idea per item instead of 2
python scripts/generate_repertoire.py --exhaust --ideas-per-item 1
```

---

## 2. Trending News Ideas — `generate_from_trending.py`

Generate content ideas from recent food-safety news (uses Grok for real-time awareness).

### Flags

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--count` | int | 3 | Number of ideas to generate |
| `--days` | int | 7 | How many days back to search for news |
| `--screenplays` / `--no-screenplays` | bool | True | Also generate screenplays |

### Examples

```bash
python scripts/generate_from_trending.py --count 3 --days 7
```

---

## 3. Animations — `generate_animation.py`

Generate shooting-guide animations (storyboard images stitched into MP4) from screenplays.

### Flags

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--screenplay` | path | None | Path to a single screenplay `.md` file |
| `--output` | str | None | Output filename (without extension) |
| `--mode` | `auto\|veo\|storyboard\|manim` | `auto` | Generation mode (see below) |
| `--all` | flag | False | Process ALL screenplays in the selected language folder(s) |
| `--lang` | `en\|es\|both` | `en` | Language folder to process |
| `--limit` | int | 0 | Max screenplays to generate (0 = unlimited) |
| `--force` | flag | False | Re-generate even if animation already exists |
| `--voice` | `nova\|alloy\|echo\|fable\|onyx\|shimmer` | None | Add TTS voiceover (omit for silent) |
| `--add-voice` | flag | False | Overlay TTS on EXISTING animations (no image re-generation) |

### Animation Modes

| Mode | What it does |
|------|-------------|
| `auto` | Try Veo → Imagen → DALL-E → Manim (best available) |
| `veo` | Gemini Veo AI video per scene |
| `storyboard` | DALL-E 3 images stitched into video (recommended) |
| `manim` | Offline stick-figure animation (no API needed) |

### Examples

```bash
# Single screenplay
python scripts/generate_animation.py --screenplay data/generated/screenplays/en/some_file.md --mode storyboard

# Batch: all EN screenplays
python scripts/generate_animation.py --all --mode storyboard

# Test with 1 first
python scripts/generate_animation.py --all --mode storyboard --limit 1

# Both languages
python scripts/generate_animation.py --all --mode storyboard --lang both

# With voice baked in
python scripts/generate_animation.py --all --mode storyboard --voice nova
```

### Recommended Two-Step Workflow (avoids duplicating image generation)

```bash
# Step 1: Generate silent base animations (EN only — images are language-independent)
python scripts/generate_animation.py --all --mode storyboard

# Step 2: Overlay voice on existing videos (cheap — only LLM parse + TTS)
python scripts/generate_animation.py --add-voice --voice nova --lang en    # English voice
python scripts/generate_animation.py --add-voice --voice nova --lang es    # Spanish voice
python scripts/generate_animation.py --add-voice --voice nova --lang both  # Both at once
```

---

## Typical Workflows

| Goal | Command(s) |
|------|------------|
| Bootstrap all content from seed data | `generate_repertoire.py --exhaust` |
| Ideas only, skip screenplays | `generate_repertoire.py --exhaust --no-screenplays` |
| React to breaking news | `generate_from_trending.py --count 3 --days 3` |
| Redo everything from scratch | `generate_repertoire.py --reset-coverage --exhaust` |
| Generate all animations | `generate_animation.py --all --mode storyboard` |
| Test animation pipeline | `generate_animation.py --all --mode storyboard --limit 1` |
| Add voice to existing videos | `generate_animation.py --add-voice --voice nova --lang both` |

---

## Output Directory Structure

```
data/generated/
├── coverage_log.json           # Tracks which seed items have been covered
├── ideas/                      # JSON files, one per LLM batch call
│   └── ideas_YYYYMMDD_HHMMSS.json
├── screenplays/
│   ├── en/                     # English screenplays (.md)
│   └── es/                     # Spanish screenplays (.md)
└── animations/                 # MP4 shooting guide videos
    ├── *_shooting_guide_en.mp4
    └── *_shooting_guide_es.mp4
```

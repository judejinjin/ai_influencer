"""
Generate a batch of content ideas and bilingual screenplays.

Usage:
    python scripts/generate_repertoire.py --count 10 --pillar all
    python scripts/generate_repertoire.py --exhaust          # Cover ALL seed data
    python scripts/generate_repertoire.py --exhaust --no-screenplays  # Ideas only
"""
import json
import sys
import time
import click
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generators.idea_generator import generate_ideas
from src.generators.screenplay_writer import write_screenplay
from src.config import GENERATED_DIR
from src.research.food_database import (
    get_random_comparisons, get_random_deep_dives,
    get_all_comparisons, get_all_deep_dives,
    get_all_staples, format_staple_for_prompt,
    format_for_prompt as format_food,
)
from src.research.regulation_research import (
    get_banned_additives, get_timeline_events, get_obesity_stats,
    get_all_additives, get_all_timeline_events,
    format_for_prompt as format_reg,
)

# ── Duplicate tracking ────────────────────────────────────────
COVERAGE_FILE = GENERATED_DIR / "coverage_log.json"


def _load_coverage() -> dict:
    """Load record of which seed data items have been used."""
    if COVERAGE_FILE.exists():
        cov = json.loads(COVERAGE_FILE.read_text(encoding="utf-8"))
        cov.setdefault("staples", [])  # ensure new key exists in old files
        return cov
    return {"comparisons": [], "deep_dives": [], "additives": [], "events": [], "staples": []}


def _save_coverage(cov: dict):
    COVERAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    COVERAGE_FILE.write_text(
        json.dumps(cov, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _item_key(item: dict) -> str:
    """Create a unique key for a seed data item."""
    if item.get("id"):  # daily staple
        return item["id"]
    elif item.get("type") == "comparison":
        return item.get("healthy_option", "")[:60]
    elif item.get("type") == "deep-dive":
        return item.get("ingredient", "")
    elif item.get("name"):  # additive
        return item["name"]
    elif item.get("event"):  # timeline event
        return f"{item.get('year', '')}_{item['event'][:40]}"
    return str(item)[:60]


# ── Exhaust mode ──────────────────────────────────────────────
def run_exhaust(screenplays: bool, ideas_per_item: int):
    """
    Systematically generate ideas for EVERY item in the seed database.
    Each food fact, additive, and timeline event gets its own focused batch.
    Tracks coverage so re-running skips already-covered items.
    """
    coverage = _load_coverage()
    all_ideas = []
    total_generated = 0

    # ── 1. Comparison pillar: one batch per food comparison ────
    comparisons = get_all_comparisons()
    uncovered_comp = [
        c for c in comparisons
        if _item_key(c) not in coverage["comparisons"]
    ]
    if uncovered_comp:
        click.echo(f"\n🥗 COMPARISON pillar: {len(uncovered_comp)} items "
                    f"({len(comparisons) - len(uncovered_comp)} already covered)\n")
        for i, comp in enumerate(uncovered_comp, 1):
            label = f"{comp['healthy_option']} vs {comp['processed_option']}"
            click.echo(f"  [{i}/{len(uncovered_comp)}] {label}")
            food_ctx = format_food([comp])
            ideas = generate_ideas(
                count=ideas_per_item,
                pillar="comparison",
                food_context=food_ctx,
            )
            all_ideas.extend(ideas)
            total_generated += len(ideas)
            coverage["comparisons"].append(_item_key(comp))
            _save_coverage(coverage)
            time.sleep(2)  # rate-limit courtesy
    else:
        click.echo("\n🥗 COMPARISON pillar: ✅ All items already covered")

    # ── 2. Deep-dive pillar: one batch per ingredient ──────────
    deep_dives = get_all_deep_dives()
    uncovered_dd = [
        d for d in deep_dives
        if _item_key(d) not in coverage["deep_dives"]
    ]
    if uncovered_dd:
        click.echo(f"\n🔬 DEEP-DIVE pillar: {len(uncovered_dd)} items "
                    f"({len(deep_dives) - len(uncovered_dd)} already covered)\n")
        for i, dd in enumerate(uncovered_dd, 1):
            click.echo(f"  [{i}/{len(uncovered_dd)}] {dd['ingredient']}")
            food_ctx = format_food([dd])
            ideas = generate_ideas(
                count=ideas_per_item,
                pillar="deep-dive",
                food_context=food_ctx,
            )
            all_ideas.extend(ideas)
            total_generated += len(ideas)
            coverage["deep_dives"].append(_item_key(dd))
            _save_coverage(coverage)
            time.sleep(2)  # rate-limit courtesy
    else:
        click.echo("\n🔬 DEEP-DIVE pillar: ✅ All items already covered")

    # ── 3. Regulation pillar: one batch per additive ───────────
    additives = get_all_additives()
    uncovered_add = [
        a for a in additives
        if _item_key(a) not in coverage["additives"]
    ]
    if uncovered_add:
        click.echo(f"\n⚖️  REGULATION pillar (additives): {len(uncovered_add)} items "
                    f"({len(additives) - len(uncovered_add)} already covered)\n")
        for i, add in enumerate(uncovered_add, 1):
            click.echo(f"  [{i}/{len(uncovered_add)}] {add['name']}")
            reg_ctx = format_reg(additives=[add], stats=get_obesity_stats())
            ideas = generate_ideas(
                count=ideas_per_item,
                pillar="regulation",
                regulation_context=reg_ctx,
            )
            all_ideas.extend(ideas)
            total_generated += len(ideas)
            coverage["additives"].append(_item_key(add))
            _save_coverage(coverage)
            time.sleep(2)  # rate-limit courtesy
    else:
        click.echo("\n⚖️  REGULATION pillar (additives): ✅ All items already covered")

    # ── 4. Regulation pillar: one batch per timeline event ─────
    events = get_all_timeline_events()
    uncovered_ev = [
        e for e in events
        if _item_key(e) not in coverage["events"]
    ]
    if uncovered_ev:
        click.echo(f"\n📜 REGULATION pillar (timeline): {len(uncovered_ev)} items "
                    f"({len(events) - len(uncovered_ev)} already covered)\n")
        for i, ev in enumerate(uncovered_ev, 1):
            click.echo(f"  [{i}/{len(uncovered_ev)}] {ev['year']}: {ev['event'][:60]}")
            reg_ctx = format_reg(events=[ev], stats=get_obesity_stats())
            ideas = generate_ideas(
                count=ideas_per_item,
                pillar="regulation",
                regulation_context=reg_ctx,
            )
            all_ideas.extend(ideas)
            total_generated += len(ideas)
            coverage["events"].append(_item_key(ev))
            _save_coverage(coverage)
            time.sleep(2)  # rate-limit courtesy
    else:
        click.echo("\n📜 REGULATION pillar (timeline): ✅ All items already covered")

    # ── 5. Daily staples pillar: one batch per staple topic ───
    staples = get_all_staples()
    uncovered_st = [
        s for s in staples
        if _item_key(s) not in coverage["staples"]
    ]
    if uncovered_st:
        click.echo(f"\n🛒 DAILY STAPLES pillar: {len(uncovered_st)} items "
                    f"({len(staples) - len(uncovered_st)} already covered)\n")
        for i, st in enumerate(uncovered_st, 1):
            label = f"[{st.get('category', '')}] {st['id']}"
            click.echo(f"  [{i}/{len(uncovered_st)}] {label}")
            staple_ctx = format_staple_for_prompt(st)
            ideas = generate_ideas(
                count=ideas_per_item,
                pillar="comparison",
                food_context=staple_ctx,
            )
            all_ideas.extend(ideas)
            total_generated += len(ideas)
            coverage["staples"].append(_item_key(st))
            _save_coverage(coverage)
            time.sleep(2)  # rate-limit courtesy
    else:
        click.echo("\n🛒 DAILY STAPLES pillar: ✅ All items already covered")

    # ── Summary ────────────────────────────────────────────────
    click.echo(f"\n{'='*50}")
    click.echo(f"📊 EXHAUST SUMMARY")
    click.echo(f"   Total ideas generated: {total_generated}")
    click.echo(f"   Coverage: "
               f"{len(coverage['comparisons'])}/{len(comparisons)} comparisons, "
               f"{len(coverage['deep_dives'])}/{len(deep_dives)} deep-dives, "
               f"{len(coverage['additives'])}/{len(additives)} additives, "
               f"{len(coverage['events'])}/{len(events)} events, "
               f"{len(coverage['staples'])}/{len(staples)} staples")
    click.echo(f"{'='*50}")

    # ── Generate screenplays for all ideas ─────────────────────
    if screenplays and all_ideas:
        click.echo(f"\n📝 Generating bilingual screenplays for {len(all_ideas)} ideas...\n")
        for i, idea in enumerate(all_ideas, 1):
            title = idea.get("title_en", idea.get("title", "Untitled"))
            click.echo(f"  Writing screenplay {i}/{len(all_ideas)}: {title}...")
            result = write_screenplay(
                idea=idea,
                food_context=idea.get("_source_food_context", ""),
                regulation_context=idea.get("_source_regulation_context", ""),
            )
            click.echo(f"    → EN: {result['en_path']}")
            click.echo(f"    → ES: {result['es_path']}")

    if total_generated == 0:
        click.echo("\n✅ All seed data has been covered! Run with --reset-coverage "
                    "to start fresh, or add more entries to the seed data files.")
    else:
        click.echo(f"\n🎉 Done! {total_generated} ideas generated. "
                    f"Check data/generated/ for output.\n")

    return all_ideas


# ── CLI ───────────────────────────────────────────────────────
@click.command()
@click.option("--count", default=5, help="Number of ideas to generate (ignored with --exhaust)")
@click.option(
    "--pillar", default="all",
    type=click.Choice(["all", "comparison", "deep-dive", "regulation", "trending"]),
)
@click.option(
    "--screenplays/--no-screenplays", default=True,
    help="Also generate full screenplays for each idea",
)
@click.option(
    "--exhaust", is_flag=True, default=False,
    help="Systematically cover ALL seed data items (ignores --count and --pillar)",
)
@click.option(
    "--ideas-per-item", default=2,
    help="Number of ideas to generate per seed data item in --exhaust mode",
)
@click.option(
    "--reset-coverage", is_flag=True, default=False,
    help="Clear the coverage log and start fresh",
)
def main(count, pillar, screenplays, exhaust, ideas_per_item, reset_coverage):
    """Generate a repertoire of content ideas and bilingual screenplays."""

    if reset_coverage:
        if COVERAGE_FILE.exists():
            COVERAGE_FILE.unlink()
            click.echo("🗑️  Coverage log reset. All items will be re-covered.\n")
        else:
            click.echo("ℹ️  No coverage log found — nothing to reset.\n")
        if not exhaust:
            return

    if exhaust:
        click.echo("\n🔄 EXHAUST MODE — covering all seed data systematically\n")
        run_exhaust(screenplays=screenplays, ideas_per_item=ideas_per_item)
        return

    # ── Normal mode (original behavior) ───────────────────────
    click.echo(f"\n🎬 Generating {count} ideas (pillar: {pillar})...\n")

    food_context = format_food(
        get_random_comparisons(5) + get_random_deep_dives(5)
    )
    reg_context = format_reg(
        additives=get_banned_additives(5),
        events=get_timeline_events(5),
        stats=get_obesity_stats(),
    )

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

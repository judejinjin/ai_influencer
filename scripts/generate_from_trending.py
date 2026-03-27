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
    get_banned_additives, get_timeline_events,
    format_for_prompt as format_reg,
)


@click.command()
@click.option("--count", default=3, help="Number of ideas to generate")
@click.option("--days", default=7, help="How many days back to search for news")
@click.option("--screenplays/--no-screenplays", default=True)
def main(count, days, screenplays):
    """Generate content ideas from trending food-safety news."""

    click.echo(f"\n📰 Fetching trending food-safety news (last {days} days)...\n")
    articles = fetch_trending_news(days=days)
    click.echo(f"  Found {len(articles)} articles")

    if not articles:
        click.echo("  ⚠️  No trending news found. Try increasing --days.")
        return

    for a in articles[:5]:
        click.echo(f"  • [{a['date']}] {a['title']}")

    # Build context
    news_context = format_news(articles, count=8)
    reg_context = format_reg(
        additives=get_banned_additives(3),
        events=get_timeline_events(3),
    )

    # Generate ideas — uses Grok for real-time news awareness
    click.echo(f"\n🎬 Generating {count} trending-reactive ideas (via Grok)...\n")
    ideas = generate_ideas(
        count=count,
        pillar="trending",
        news_context=news_context,
        regulation_context=reg_context,
        provider="grok",
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

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
        data = _get_default_regulation_data()
        REGULATION_PATH.parent.mkdir(parents=True, exist_ok=True)
        REGULATION_PATH.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return data
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


def get_all_additives() -> list[dict]:
    """Return ALL banned additive entries."""
    data = load_regulation_data()
    return data.get("banned_additives", [])


def get_all_timeline_events() -> list[dict]:
    """Return ALL timeline event entries."""
    data = load_regulation_data()
    return data.get("timeline", [])


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
            lines.append(
                f"  • {s['year']}: {s['rate']}% (adults), "
                f"{s.get('children_rate', 'N/A')}% (children)"
            )
    return "\n".join(lines)


def _get_default_regulation_data() -> dict:
    """Hardcoded seed data — written to disk on first run."""
    return {
        "banned_additives": [
            {
                "name": "Red Dye 3 (Erythrosine)",
                "used_in": "Candy, baked goods, maraschino cherries",
                "banned_in": ["EU (partially)", "Austria", "Norway"],
                "health_concern": "Linked to thyroid tumors in animal studies; FDA acknowledged carcinogenicity in 1990 but only banned in cosmetics",
                "year_concern_raised": 1990,
            },
            {
                "name": "Potassium Bromate",
                "used_in": "Bread, flour, baked goods",
                "banned_in": ["EU", "UK", "Canada", "Brazil", "China"],
                "health_concern": "Classified as possibly carcinogenic (Group 2B) by IARC",
                "year_concern_raised": 1999,
            },
            {
                "name": "BHA (Butylated Hydroxyanisole)",
                "used_in": "Cereals, snack foods, chewing gum, butter",
                "banned_in": ["EU (restricted)", "Japan"],
                "health_concern": "Reasonably anticipated to be a human carcinogen (NTP)",
                "year_concern_raised": 2011,
            },
            {
                "name": "Azodicarbonamide",
                "used_in": "Bread (as dough conditioner) — also used in yoga mats/shoe soles",
                "banned_in": ["EU", "Australia", "Singapore"],
                "health_concern": "Breaks down into semicarbazide (possible carcinogen) during baking",
                "year_concern_raised": 2005,
            },
            {
                "name": "Titanium Dioxide (E171)",
                "used_in": "Candy, coffee creamer, frosting, supplements",
                "banned_in": ["EU (banned 2022)"],
                "health_concern": "Potential genotoxicity — can damage DNA per EFSA assessment",
                "year_concern_raised": 2021,
            },
            {
                "name": "BHT (Butylated Hydroxytoluene)",
                "used_in": "Cereals, snack foods, packaging materials",
                "banned_in": ["UK", "EU (restricted in food contact)"],
                "health_concern": "Possible endocrine disruptor; linked to liver and kidney damage in animal studies",
                "year_concern_raised": 2002,
            },
            {
                "name": "rBGH / rBST (Recombinant Bovine Growth Hormone)",
                "used_in": "Dairy products (injected into cows to increase milk production)",
                "banned_in": ["EU", "Canada", "Australia", "Japan", "Israel"],
                "health_concern": "Increases IGF-1 levels in milk — linked to increased cancer risk",
                "year_concern_raised": 1993,
            },
            {
                "name": "Ractopamine",
                "used_in": "Pork, beef, turkey (growth promoter in livestock)",
                "banned_in": ["EU", "China", "Russia", "160+ countries"],
                "health_concern": "Cardiovascular effects; residues in meat may affect heart rate",
                "year_concern_raised": 2002,
            },
            {
                "name": "Yellow 5 (Tartrazine) & Yellow 6 (Sunset Yellow)",
                "used_in": "Candy, cereals, sodas, sports drinks, mac & cheese",
                "banned_in": ["Norway", "Finland (restricted)", "Austria"],
                "health_concern": "EU requires warning labels — 'may have adverse effect on activity and attention in children'",
                "year_concern_raised": 2007,
            },
            {
                "name": "Brominated Vegetable Oil (BVO)",
                "used_in": "Sodas, sports drinks (emulsifier for citrus flavoring)",
                "banned_in": ["EU", "Japan", "India"],
                "health_concern": "Bromine accumulates in body tissue; linked to neurological and thyroid issues. FDA proposed ban in 2023",
                "year_concern_raised": 2014,
            },
        ],
        "timeline": [
            {
                "year": 1906,
                "event": "Pure Food and Drug Act signed — first federal food safety law",
                "impact": "Banned mislabeled food but lacked enforcement power",
            },
            {
                "year": 1938,
                "event": "Federal Food, Drug, and Cosmetic Act — FDA gains enforcement power",
                "impact": "Required safety evidence for new drugs but food additives still loosely regulated",
            },
            {
                "year": 1958,
                "event": "Food Additives Amendment — GRAS loophole created",
                "impact": "Companies can self-certify ingredients as safe WITHOUT FDA review",
            },
            {
                "year": 1977,
                "event": "McGovern Report recommends reducing sugar/fat in American diet",
                "impact": "Food industry lobbying weakened final guidelines — focus shifted to low-fat (which led to added sugar)",
            },
            {
                "year": 1980,
                "event": "First US Dietary Guidelines issued",
                "impact": "Promoted low-fat diet; food industry began replacing fat with sugar and additives",
            },
            {
                "year": 1992,
                "event": "USDA Food Pyramid released",
                "impact": "Heavily influenced by grain/dairy industry lobbying — recommended 6-11 servings of grains daily",
            },
            {
                "year": 1996,
                "event": "GRAS self-affirmation process formalized",
                "impact": "Companies no longer need to notify FDA before adding new chemicals to food",
            },
            {
                "year": 2015,
                "event": "FDA removes trans fats (partially hydrogenated oils) from GRAS list",
                "impact": "Took decades of evidence — shows how slow the US system is to act",
            },
            {
                "year": 2023,
                "event": "FDA proposes ban on brominated vegetable oil (BVO)",
                "impact": "Was GRAS since 1958 — took 65 years to act; banned in EU/Japan for decades",
            },
            {
                "year": 2025,
                "event": "FDA finalizes ban on Red Dye 3 in food",
                "impact": "Known carcinogen since 1990 — took 35 years to ban in food (was banned in cosmetics in 1990)",
            },
        ],
        "obesity_stats": [
            {"year": 1960, "rate": 13.4, "children_rate": 5.0},
            {"year": 1980, "rate": 15.0, "children_rate": 5.5},
            {"year": 1994, "rate": 22.5, "children_rate": 10.0},
            {"year": 2000, "rate": 30.5, "children_rate": 13.9},
            {"year": 2010, "rate": 35.7, "children_rate": 16.9},
            {"year": 2016, "rate": 39.8, "children_rate": 18.5},
            {"year": 2020, "rate": 41.9, "children_rate": 19.7},
            {"year": 2024, "rate": 43.0, "children_rate": 21.0},
        ],
    }

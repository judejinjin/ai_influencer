"""
Formats generated content into polished output using Jinja2 templates.
"""
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from src.config import TEMPLATES_DIR

_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


def format_screenplay(screenplay_data: dict, language: str = "en") -> str:
    """Render a screenplay dict through the Jinja2 template."""
    template_name = f"screenplay_{language}.md.j2"
    template = _env.get_template(template_name)
    return template.render(**screenplay_data)

"""
Resize a headshot image to the optimal size for animation generation.

Usage:
    python scripts/resize_headshot.py data/wm_with_glasses.jpg
    python scripts/resize_headshot.py data/wm_with_glasses.jpg --output data/wm_with_glasses_512.jpg
    python scripts/resize_headshot.py data/wm_with_glasses.jpg --max-dim 256
"""
import sys
import click
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generators.animation_generator import _HEADSHOT_MAX_DIM


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option(
    "--output", "-o", default=None,
    help="Output path. Default: <input>_<dim>.jpg next to the original.",
)
@click.option(
    "--max-dim", default=_HEADSHOT_MAX_DIM, type=int,
    help=f"Maximum dimension in pixels (default: {_HEADSHOT_MAX_DIM}).",
)
@click.option(
    "--quality", default=85, type=int,
    help="JPEG quality 1-100 (default: 85).",
)
def main(input_path, output, max_dim, quality):
    """Resize a headshot image for use with --headshot in generate_animation.py."""
    from PIL import Image as PILImage

    img = PILImage.open(input_path)
    original_size = img.size
    original_bytes = Path(input_path).stat().st_size

    if max(img.size) <= max_dim and input_path.lower().endswith((".jpg", ".jpeg")):
        click.echo(f"Already optimal: {img.size[0]}x{img.size[1]} (<= {max_dim}px)")
        click.echo(f"  {input_path} ({original_bytes // 1024}KB)")
        return

    img.thumbnail((max_dim, max_dim))
    if img.mode == "RGBA":
        img = img.convert("RGB")

    if not output:
        p = Path(input_path)
        output = str(p.parent / f"{p.stem}_{max_dim}{'.jpg'}")

    img.save(output, format="JPEG", quality=quality)
    new_bytes = Path(output).stat().st_size

    click.echo(f"Resized: {original_size[0]}x{original_size[1]} → {img.size[0]}x{img.size[1]}")
    click.echo(f"  {original_bytes // 1024}KB → {new_bytes // 1024}KB")
    click.echo(f"  Saved to: {output}")


if __name__ == "__main__":
    main()

"""
Standalone script to generate shooting guide animations from screenplays.

Usage:
    python scripts/generate_animation.py --screenplay path/to/screenplay.md
    python scripts/generate_animation.py --screenplay path/to/screenplay.md --mode storyboard
    python scripts/generate_animation.py --all --mode storyboard --limit 3   # batch, test 3 first
    python scripts/generate_animation.py --all --mode storyboard --lang es   # Spanish screenplays
    python scripts/generate_animation.py --all --mode storyboard --lang both # EN + ES

    # Generate silent base animations, then overlay voice separately:
    python scripts/generate_animation.py --all --mode storyboard             # step 1: images (EN)
    python scripts/generate_animation.py --add-voice --voice nova --lang both # step 2: TTS only
"""
import sys
import click
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generators.animation_generator import generate_shooting_guide, add_voice_to_video
from src.config import SCREENPLAYS_EN_DIR, SCREENPLAYS_ES_DIR, ANIMATIONS_DIR


def _already_generated(screenplay_path: Path, lang: str) -> bool:
    """Check if a shooting guide animation already exists for this screenplay."""
    expected_name = screenplay_path.stem + f"_shooting_guide_{lang}.mp4"
    return (ANIMATIONS_DIR / expected_name).exists()


def _get_screenplay_dir(lang: str) -> Path:
    return {"en": SCREENPLAYS_EN_DIR, "es": SCREENPLAYS_ES_DIR}[lang]


@click.command()
@click.option(
    "--screenplay", default=None, type=click.Path(exists=True),
    help="Path to a single screenplay .md file",
)
@click.option("--output", default=None, help="Output filename (without extension)")
@click.option(
    "--mode", default="auto",
    type=click.Choice(["auto", "veo", "storyboard", "manim"]),
    help="Generation mode: auto (try best→fallback), veo (Gemini video), "
         "storyboard (Imagen/DALL-E frames), manim (offline stick-figure)",
)
@click.option(
    "--all", "process_all", is_flag=True, default=False,
    help="Process ALL screenplays in the selected language folder(s)",
)
@click.option(
    "--lang", default="both",
    type=click.Choice(["en", "es", "both"]),
    help="Language: en (English), es (Spanish), both (default: EN + ES)",
)
@click.option(
    "--limit", default=0, type=int,
    help="Max number of screenplays to generate (0 = unlimited). Great for testing.",
)
@click.option(
    "--force", is_flag=True, default=False,
    help="Re-generate even if animation already exists",
)
@click.option(
    "--voice", default="nova",
    type=click.Choice(["nova", "alloy", "echo", "fable", "onyx", "shimmer"]),
    help="TTS voice for voiceover (default: nova = warm female). "
         "Used with --add-voice or during animation generation.",
)
@click.option(
    "--add-voice", "add_voice", is_flag=True, default=False,
    help="Overlay TTS on EXISTING animations (no image re-generation). "
         "Requires --voice. Uses EN base animations + screenplays for --lang.",
)
def main(screenplay, output, mode, process_all, lang, limit, force, voice, add_voice):
    """Generate shooting guide animations from screenplays."""

    if not screenplay and not process_all and not add_voice:
        click.echo("Error: provide --screenplay PATH, --all, or --add-voice.")
        raise SystemExit(1)

    # ── Add voice to existing animations ───────────────────────
    if add_voice:
        if not voice:
            click.echo("Error: --add-voice requires --voice (e.g. --voice nova)")
            raise SystemExit(1)

        langs = ["en", "es"] if lang == "both" else [lang]

        # Base animations are always EN (visuals are language-independent)
        base_pattern = "*_shooting_guide_en.mp4"
        base_animations = sorted(ANIMATIONS_DIR.glob(base_pattern))
        if not base_animations:
            click.echo(f"\nNo base EN animations found in {ANIMATIONS_DIR}")
            click.echo("Generate animations first: --all --mode storyboard")
            raise SystemExit(1)

        for target_lang in langs:
            sp_dir = _get_screenplay_dir(target_lang)
            batch = base_animations[:limit] if limit > 0 else base_animations

            click.echo(f"\n🗣️  ADD VOICE — {target_lang.upper()} (voice: {voice})")
            click.echo(f"   Base animations: {len(base_animations)}")
            click.echo(f"   To process: {len(batch)}"
                       + (f" (limited to {limit})" if limit > 0 else ""))
            click.echo()

            success = 0
            failed = 0
            skipped = 0

            for i, base_mp4 in enumerate(batch, 1):
                stem = base_mp4.stem.replace("_shooting_guide_en", "")
                screenplay_file = sp_dir / f"{stem}.md"

                if not screenplay_file.exists():
                    click.echo(f"  [{i}/{len(batch)}] {stem}: ⚠️  no {target_lang.upper()} screenplay")
                    skipped += 1
                    continue

                out_path = ANIMATIONS_DIR / f"{stem}_shooting_guide_{target_lang}.mp4"
                if out_path.exists() and not force:
                    click.echo(f"  [{i}/{len(batch)}] {stem}: ⏭️  already exists")
                    skipped += 1
                    continue

                click.echo(f"  [{i}/{len(batch)}] {stem}")
                try:
                    result = add_voice_to_video(
                        video_path=str(base_mp4),
                        screenplay_path=str(screenplay_file),
                        voice=voice,
                        output_path=str(out_path),
                    )
                    click.echo(f"    ✅ {result}")
                    success += 1
                except Exception as e:
                    click.echo(f"    ❌ Failed: {e}")
                    failed += 1

            click.echo(f"\n{'='*50}")
            click.echo(f"📊 VOICE {target_lang.upper()}: {success} voiced, "
                       f"{failed} failed, {skipped} skipped")
            click.echo(f"{'='*50}")
        return

    # ── Single screenplay mode ─────────────────────────────────
    if screenplay and not process_all:
        sp = Path(screenplay)
        # Detect language from path
        sp_lang = "es" if "/es/" in str(sp) else "en"
        if not force and _already_generated(sp, sp_lang):
            click.echo(f"\n⏭️  Already generated: {sp.stem} (use --force to redo)")
            return
        out_name = output or (sp.stem + f"_shooting_guide_{sp_lang}")
        click.echo(f"\n🎬 Generating shooting guide animation (mode: {mode}, lang: {sp_lang}"
                   + (f", voice: {voice}" if voice else "") + ")...")
        click.echo(f"  Screenplay: {screenplay}")
        result_path = generate_shooting_guide(
            screenplay_path=screenplay,
            output_name=out_name,
            mode=mode,
            voice=voice,
        )
        click.echo(f"\n✅ Shooting guide saved to: {result_path}\n")
        return

    # ── Batch mode (--all) ─────────────────────────────────────
    # When --lang both, generate EN fully (images + TTS + stitch) then
    # reuse EN video for ES by overlaying ES TTS — avoids regenerating images.
    do_both = lang == "both"
    primary_lang = "en"  # always generate images for EN

    # ── Pass 1: generate primary language (EN) fully ───────────
    if do_both or lang == "en":
        _batch_generate(primary_lang, mode, voice, limit, force)

    # ── Pass 2: overlay second language TTS on EN base videos ──
    if do_both or lang == "es":
        if do_both:
            # Reuse EN animations as base, overlay ES voiceover only
            _batch_voice_overlay("es", voice, limit, force)
        else:
            # Standalone ES: generate from scratch
            _batch_generate("es", mode, voice, limit, force)


def _batch_generate(current_lang, mode, voice, limit, force):
    """Full generation: images + TTS + stitch for a single language."""
    sp_dir = _get_screenplay_dir(current_lang)
    screenplays_list = sorted(sp_dir.glob("*.md"))
    if not screenplays_list:
        click.echo(f"\nNo screenplays found in {sp_dir}")
        return

    if not force:
        pending = [sp for sp in screenplays_list
                   if not _already_generated(sp, current_lang)]
    else:
        pending = list(screenplays_list)

    skipped = len(screenplays_list) - len(pending)
    batch = pending[:limit] if limit > 0 else pending

    click.echo(f"\n🎬 BATCH ANIMATION — {current_lang.upper()} (mode: {mode}"
               + (f", voice: {voice}" if voice else "") + ")")
    click.echo(f"   Total screenplays: {len(screenplays_list)}")
    click.echo(f"   Already generated: {skipped} (skipped)")
    click.echo(f"   To process: {len(batch)}"
               + (f" (limited to {limit})" if limit > 0 else ""))
    click.echo()

    generated = 0
    failed = 0
    for i, sp in enumerate(batch, 1):
        click.echo(f"  [{i}/{len(batch)}] {sp.stem}")
        try:
            out_name = sp.stem + f"_shooting_guide_{current_lang}"
            result_path = generate_shooting_guide(
                screenplay_path=str(sp),
                output_name=out_name,
                mode=mode,
                voice=voice,
            )
            click.echo(f"    ✅ {result_path}")
            generated += 1
        except Exception as e:
            click.echo(f"    ❌ Failed: {e}")
            failed += 1

    click.echo(f"\n{'='*50}")
    click.echo(f"📊 {current_lang.upper()} SUMMARY: {generated} generated, "
               f"{failed} failed, {skipped} skipped")
    click.echo(f"{'='*50}")


def _batch_voice_overlay(target_lang, voice, limit, force):
    """Overlay TTS on existing EN base animations (no image re-generation)."""
    base_pattern = "*_shooting_guide_en.mp4"
    base_animations = sorted(ANIMATIONS_DIR.glob(base_pattern))
    if not base_animations:
        click.echo(f"\n⚠️  No EN base animations found — falling back to full generation")
        _batch_generate(target_lang, "storyboard", voice, limit, force)
        return

    sp_dir = _get_screenplay_dir(target_lang)
    batch = base_animations[:limit] if limit > 0 else base_animations

    click.echo(f"\n🗣️  VOICE OVERLAY — {target_lang.upper()} (reusing EN images, voice: {voice})")
    click.echo(f"   EN base animations: {len(base_animations)}")
    click.echo(f"   To process: {len(batch)}"
               + (f" (limited to {limit})" if limit > 0 else ""))
    click.echo()

    success = 0
    failed = 0
    skipped = 0

    for i, base_mp4 in enumerate(batch, 1):
        stem = base_mp4.stem.replace("_shooting_guide_en", "")
        screenplay_file = sp_dir / f"{stem}.md"

        if not screenplay_file.exists():
            click.echo(f"  [{i}/{len(batch)}] {stem}: ⚠️  no {target_lang.upper()} screenplay")
            skipped += 1
            continue

        out_path = ANIMATIONS_DIR / f"{stem}_shooting_guide_{target_lang}.mp4"
        if out_path.exists() and not force:
            click.echo(f"  [{i}/{len(batch)}] {stem}: ⏭️  already exists")
            skipped += 1
            continue

        click.echo(f"  [{i}/{len(batch)}] {stem}")
        try:
            result = add_voice_to_video(
                video_path=str(base_mp4),
                screenplay_path=str(screenplay_file),
                voice=voice,
                output_path=str(out_path),
            )
            click.echo(f"    ✅ {result}")
            success += 1
        except Exception as e:
            click.echo(f"    ❌ Failed: {e}")
            failed += 1

    click.echo(f"\n{'='*50}")
    click.echo(f"📊 {target_lang.upper()} SUMMARY: {success} voiced, "
               f"{failed} failed, {skipped} skipped")
    click.echo(f"{'='*50}")


if __name__ == "__main__":
    main()

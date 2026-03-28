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
    "--voice", default="auto",
    help="Edge TTS voice (default: auto = en-US-JennyNeural / es-MX-DaliaNeural). "
         "Use 'auto' for language-based selection, or a specific Edge TTS voice name.",
)
@click.option(
    "--add-voice", "add_voice", is_flag=True, default=False,
    help="Overlay TTS on EXISTING animations (no image re-generation). "
         "Requires --voice. Uses EN base animations + screenplays for --lang.",
)
@click.option(
    "--headshot", default=None, type=click.Path(exists=True),
    help="Path to a headshot image (e.g. data/wm_with_glasses.jpg). "
         "When provided, your face appears in every storyboard slide.",
)
def main(screenplay, output, mode, process_all, lang, limit, force, voice, add_voice, headshot):
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
            headshot=headshot,
        )
        click.echo(f"\n✅ Shooting guide saved to: {result_path}\n")
        return

    # ── Batch mode (--all) ─────────────────────────────────────
    # When --lang both, generate EN then immediately overlay ES for each
    # screenplay — ensures complete EN+ES pairs even if the run is interrupted.
    do_both = lang == "both"

    if do_both:
        _batch_generate_both(mode, voice, limit, force, headshot)
    elif lang == "en":
        _batch_generate("en", mode, voice, limit, force, headshot)
    elif lang == "es":
        _batch_generate("es", mode, voice, limit, force, headshot)


def _batch_generate_both(mode, voice, limit, force, headshot=None):
    """Generate silent base video, then overlay EN and ES voices separately."""
    en_dir = _get_screenplay_dir("en")
    es_dir = _get_screenplay_dir("es")
    screenplays_list = sorted(en_dir.glob("*.md"))
    if not screenplays_list:
        click.echo(f"\nNo screenplays found in {en_dir}")
        return

    if not force:
        # Skip only when BOTH en and es already exist
        pending = [sp for sp in screenplays_list
                   if not _already_generated(sp, "en") or not _already_generated(sp, "es")]
    else:
        pending = list(screenplays_list)

    skipped = len(screenplays_list) - len(pending)
    batch = pending[:limit] if limit > 0 else pending

    click.echo(f"\n🎬 BATCH ANIMATION — EN+ES (mode: {mode}"
               + (f", voice: {voice}" if voice else "") + ")")
    click.echo(f"   Total screenplays: {len(screenplays_list)}")
    click.echo(f"   Already complete (EN+ES): {skipped} (skipped)")
    click.echo(f"   To process: {len(batch)}"
               + (f" (limited to {limit})" if limit > 0 else ""))
    click.echo()

    en_generated = 0
    es_generated = 0
    failed = 0

    for i, sp in enumerate(batch, 1):
        stem = sp.stem
        click.echo(f"  [{i}/{len(batch)}] {stem}")

        en_path = ANIMATIONS_DIR / f"{stem}_shooting_guide_en.mp4"
        es_screenplay = es_dir / f"{stem}.md"
        es_path = ANIMATIONS_DIR / f"{stem}_shooting_guide_es.mp4"
        base_path = ANIMATIONS_DIR / f"_silent_base_{stem}.mp4"

        en_exists = en_path.exists() and not force
        es_exists = es_path.exists() and not force

        if en_exists and es_exists:
            click.echo(f"    🇺🇸 EN: ⏭️  already exists")
            click.echo(f"    🇪🇸 ES: ⏭️  already exists")
            continue

        # ── Generate silent base video (no voice) ────────────
        if not base_path.exists() or force:
            try:
                out_name = f"_silent_base_{stem}"
                generate_shooting_guide(
                    screenplay_path=str(sp),
                    output_name=out_name,
                    mode=mode,
                    voice=None,       # silent — no TTS
                    headshot=headshot,
                )
                click.echo(f"    🎞️  Silent base: ✅")
            except Exception as e:
                click.echo(f"    🎞️  Silent base: ❌ Failed: {e}")
                failed += 1
                continue

        # ── EN: overlay English voice on silent base ──────────
        if en_exists:
            click.echo(f"    🇺🇸 EN: ⏭️  already exists")
        else:
            try:
                add_voice_to_video(
                    video_path=str(base_path),
                    screenplay_path=str(sp),
                    voice=voice,
                    output_path=str(en_path),
                )
                click.echo(f"    🇺🇸 EN: ✅ {en_path}")
                en_generated += 1
            except Exception as e:
                click.echo(f"    🇺🇸 EN: ❌ Failed: {e}")
                failed += 1

        # ── ES: overlay Spanish voice on silent base ──────────
        if not es_screenplay.exists():
            click.echo(f"    🇪🇸 ES: ⚠️  no ES screenplay")
        elif es_exists:
            click.echo(f"    🇪🇸 ES: ⏭️  already exists")
        else:
            try:
                add_voice_to_video(
                    video_path=str(base_path),
                    screenplay_path=str(es_screenplay),
                    voice=voice,
                    output_path=str(es_path),
                )
                click.echo(f"    🇪🇸 ES: ✅ {es_path}")
                es_generated += 1
            except Exception as e:
                click.echo(f"    🇪🇸 ES: ❌ Failed: {e}")
                failed += 1

        # ── Clean up silent base ──────────────────────────────
        if base_path.exists():
            base_path.unlink()

    click.echo(f"\n{'='*50}")
    click.echo(f"📊 SUMMARY: {en_generated} EN generated, {es_generated} ES voiced, "
               f"{failed} failed, {skipped} skipped")
    click.echo(f"{'='*50}")


def _batch_generate(current_lang, mode, voice, limit, force, headshot=None):
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
                headshot=headshot,
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

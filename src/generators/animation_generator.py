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
import shutil
from pathlib import Path
from google import genai
from google.genai import types as genai_types

from src.llm_client import call_llm, _strip_markdown_json
from src.persona import SYSTEM_PROMPT_ANIMATION_GUIDE
from src.config import ANIMATIONS_DIR, PROVIDERS, GEMINI_KEY, OPENAI_KEY


def _sanitize_image_prompt(prompt: str) -> str:
    """Rewrite image prompts to be storyboard-style and content-policy safe."""
    # Strip references that trigger content filters
    prompt = prompt.replace("young Latina woman", "illustrated character")
    prompt = prompt.replace("Latina woman", "illustrated character")
    prompt = prompt.replace("young woman", "illustrated character")
    return (
        f"Flat-color storyboard illustration for a cooking show. "
        f"Simple cartoon style, no photorealism. {prompt}"
    )


# ── Step 1: Parse screenplay into shot-by-shot directing data ──────

def parse_screenplay_for_animation(screenplay_path: str) -> list[dict]:
    """
    Use the LLM to extract structured shot-by-shot directing instructions.
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

Return as a JSON object with a "scenes" array. Each scene object must have:
time_code, section, duration_seconds, camera, body_position,
facial_expression, hand_action, props, text_overlay, movement,
transition_to_next, veo_prompt, imagen_prompt, voiceover

The "voiceover" field is the EXACT narration text the creator should speak
during this scene. Extract it directly from the screenplay's VOICEOVER lines.
If no voiceover exists for a scene, use an empty string.
"""

    response = call_llm(
        system_prompt=SYSTEM_PROMPT_ANIMATION_GUIDE,
        user_prompt=user_prompt,
        task="idea_generation",
    )

    cleaned = _strip_markdown_json(response)
    data = json.loads(cleaned)
    if isinstance(data, dict) and "scenes" in data:
        return data["scenes"]
    if isinstance(data, list):
        return data
    return []


# ── Step 2A: Gemini Veo — AI Video Generation ──────────────────────

def _generate_via_veo(scenes: list[dict], output_dir: Path) -> list[Path]:
    """Generate a short video clip per scene using Gemini Veo."""
    client = genai.Client(api_key=GEMINI_KEY)
    video_model = PROVIDERS["gemini"]["models"]["video"]
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

        clip_path = output_dir / f"scene_{i+1:02d}_{scene.get('section', 'SCENE')}.mp4"
        for vid in operation.result.generated_videos:
            video_data = client.files.download(file=vid.video)
            clip_path.write_bytes(video_data)
            clips.append(clip_path)
            break

    return clips


# ── Step 2B: Gemini Imagen — Storyboard Frame Images ──────────────

def _generate_via_imagen(scenes: list[dict], output_dir: Path) -> list[Path]:
    """Generate one storyboard image per scene using Gemini Imagen."""
    client = genai.Client(api_key=GEMINI_KEY)
    image_model = PROVIDERS["gemini"]["models"]["image"]
    frames = []

    for i, scene in enumerate(scenes):
        prompt = scene.get("imagen_prompt", "")
        if not prompt:
            prompt = (
                f"Storyboard frame: A young Latina woman in home kitchen. "
                f"Camera angle: {scene.get('camera', 'medium shot')}. "
                f"Position: {scene.get('body_position', '')}. "
                f"Expression: {scene.get('facial_expression', '')}. "
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


# ── Step 2C: DALL-E 3 — Alternative Storyboard Frames ─────────────

def _generate_via_dalle(scenes: list[dict], output_dir: Path) -> list[Path]:
    """Generate storyboard frames using OpenAI DALL-E 3."""
    from openai import OpenAI
    import requests as req

    client = OpenAI(api_key=OPENAI_KEY)
    frames = []

    for i, scene in enumerate(scenes):
        prompt = scene.get("imagen_prompt", "")
        if not prompt:
            prompt = (
                f"Storyboard frame for a cooking video: illustrated character "
                f"in home kitchen, {scene.get('camera', 'medium shot')}, "
                f"{scene.get('body_position', '')}, "
                f"{scene.get('facial_expression', '')}."
            )
        prompt = _sanitize_image_prompt(prompt)

        try:
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
        except Exception as e:
            print(f"      ⚠️  DALL-E scene {i+1} skipped: {e}")
            continue

    return frames


# ── Step 3: Generate TTS voiceover audio per scene ────────────────

def _generate_tts(scenes: list[dict], output_dir: Path, voice: str = "nova") -> list[Path | None]:
    """Generate TTS audio for each scene using OpenAI TTS.

    Args:
        scenes: Scene list with 'voiceover' text.
        output_dir: Directory to write .mp3 files.
        voice: OpenAI TTS voice (alloy, echo, fable, onyx, nova, shimmer).
               'nova' is a warm female voice that fits the Latina creator persona.

    Returns:
        List of audio file paths (None for scenes with no voiceover).
    """
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_KEY)
    audio_paths: list[Path | None] = []

    for i, scene in enumerate(scenes):
        text = scene.get("voiceover", "").strip()
        if not text:
            audio_paths.append(None)
            continue

        audio_path = output_dir / f"voice_{i+1:02d}_{scene.get('section', 'SCENE')}.mp3"
        try:
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
            )
            response.stream_to_file(str(audio_path))
            audio_paths.append(audio_path)
        except Exception as e:
            print(f"      \u26a0\ufe0f  TTS scene {i+1} skipped: {e}")
            audio_paths.append(None)

    return audio_paths


# ── Step 4: Stitch frames into a video with annotations ───────────

def _stitch_frames_to_video(
    frames: list[Path], scenes: list[dict], output_path: Path,
    audio_paths: list[Path | None] = None,
) -> str:
    """Combine storyboard frame images into a video using MoviePy."""
    from moviepy import (
        ImageClip, concatenate_videoclips, TextClip, CompositeVideoClip,
        AudioFileClip, CompositeAudioClip,
    )

    clips = []
    scene_audios = []
    time_cursor = 0.0

    for idx, (frame, scene) in enumerate(zip(frames, scenes)):
        duration = scene.get("duration_seconds", 3)

        # If we have audio for this scene, adjust duration to match audio length
        audio_file = audio_paths[idx] if audio_paths and idx < len(audio_paths) else None
        audio_clip = None
        if audio_file and audio_file.exists():
            audio_clip = AudioFileClip(str(audio_file))
            # Use the longer of scene duration or audio duration
            duration = max(duration, audio_clip.duration + 0.5)

        img_clip = ImageClip(str(frame), duration=duration)

        label = (
            f"[{scene.get('time_code', '')}] {scene.get('section', '')}\n"
            f"Camera: {scene.get('camera', '')}\n"
            f"Action: {scene.get('movement', 'Hold')}"
        )
        txt_clip = (
            TextClip(
                font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                text=label,
                font_size=20,
                color="yellow",
                bg_color="black",
                method="caption",
                size=(400, None),
                duration=duration,
            )
            .with_position(("left", "bottom"))
        )

        composite = CompositeVideoClip([img_clip, txt_clip])
        clips.append(composite)

        if audio_clip:
            scene_audios.append(audio_clip.with_start(time_cursor))

        time_cursor += duration

    final = concatenate_videoclips(clips, method="compose")

    # Mix all scene audio tracks into one composite and attach
    if scene_audios:
        composite_audio = CompositeAudioClip(scene_audios)
        final = final.with_audio(composite_audio)

    final.write_videofile(str(output_path), fps=24)
    return str(output_path)


# ── Step 4: Manim Fallback (offline, no API needed) ───────────────

def _generate_via_manim(scenes: list[dict], output_path: Path) -> str:
    """
    Generate a programmatic stick-figure shooting guide using Manim.
    Each scene shows: stick figure with pose, camera framing overlay,
    timing bar, and text annotations.
    """
    from manim import (
        Scene, Text, Rectangle, Line, Circle, Dot,
        VGroup, LEFT, RIGHT, UP, DOWN, ORIGIN,
        FadeIn, FadeOut, Write, Create,
        config as manim_config,
    )

    # Configure Manim output
    manim_config.output_file = output_path.stem
    manim_config.media_dir = str(output_path.parent / "_manim_media")

    class ShootingGuideScene(Scene):
        def construct(self):
            for i, scene in enumerate(scenes):
                elements = VGroup()

                # Scene header
                header = Text(
                    f"Scene {i+1}: {scene.get('section', 'SCENE')}",
                    font_size=28, color="#FFD700",
                ).to_edge(UP, buff=0.3)
                elements.add(header)

                # Time code
                time_text = Text(
                    f"[{scene.get('time_code', '?')}]  "
                    f"{scene.get('duration_seconds', 3)}s",
                    font_size=20, color="#AAAAAA",
                ).next_to(header, DOWN, buff=0.15)
                elements.add(time_text)

                # Stick figure
                head = Circle(radius=0.25, color="#FFFFFF").move_to(UP * 1.2)
                body = Line(UP * 0.95, DOWN * 0.3, color="#FFFFFF")
                l_arm = Line(UP * 0.7, LEFT * 0.6 + UP * 0.2, color="#FFFFFF")
                r_arm = Line(UP * 0.7, RIGHT * 0.6 + UP * 0.2, color="#FFFFFF")
                l_leg = Line(DOWN * 0.3, LEFT * 0.4 + DOWN * 1.0, color="#FFFFFF")
                r_leg = Line(DOWN * 0.3, RIGHT * 0.4 + DOWN * 1.0, color="#FFFFFF")
                figure = VGroup(head, body, l_arm, r_arm, l_leg, r_leg)
                figure.move_to(LEFT * 2.5 + DOWN * 0.5)
                elements.add(figure)

                # Camera framing overlay
                cam_label = scene.get("camera", "medium shot")
                if "close" in cam_label.lower():
                    frame_w, frame_h = 1.5, 1.5
                elif "wide" in cam_label.lower():
                    frame_w, frame_h = 4.0, 3.0
                else:
                    frame_w, frame_h = 2.5, 2.2
                cam_frame = Rectangle(
                    width=frame_w, height=frame_h,
                    color="#FF4444", stroke_width=2,
                ).move_to(figure.get_center() + UP * 0.3)
                cam_text = Text(
                    f"📷 {cam_label}", font_size=16, color="#FF4444",
                ).next_to(cam_frame, UP, buff=0.1)
                elements.add(cam_frame, cam_text)

                # Directing instructions (right side)
                instructions = []
                if scene.get("body_position"):
                    instructions.append(f"Body: {scene['body_position']}")
                if scene.get("facial_expression"):
                    instructions.append(f"Face: {scene['facial_expression']}")
                if scene.get("hand_action"):
                    instructions.append(f"Hands: {scene['hand_action']}")
                if scene.get("movement"):
                    instructions.append(f"Move: {scene['movement']}")

                inst_text = Text(
                    "\n".join(instructions) if instructions else "Hold position",
                    font_size=14, color="#FFFFFF",
                    line_spacing=1.3,
                ).move_to(RIGHT * 2.5)
                elements.add(inst_text)

                # Progress bar at bottom
                bar_bg = Rectangle(
                    width=10, height=0.15, color="#333333", fill_opacity=0.5,
                ).to_edge(DOWN, buff=0.3)
                progress = (i + 1) / len(scenes)
                bar_fill = Rectangle(
                    width=10 * progress, height=0.15,
                    color="#00FF88", fill_opacity=0.8,
                ).align_to(bar_bg, LEFT).to_edge(DOWN, buff=0.3)
                elements.add(bar_bg, bar_fill)

                # Animate
                self.play(FadeIn(elements), run_time=0.5)
                self.wait(scene.get("duration_seconds", 3) - 1)
                self.play(FadeOut(elements), run_time=0.5)

    # Render
    scene_obj = ShootingGuideScene()
    scene_obj.render()

    # Find and move the rendered file
    media_dir = Path(manim_config.media_dir)
    rendered_files = list(media_dir.rglob("*.mp4"))
    if rendered_files:
        shutil.move(str(rendered_files[0]), str(output_path))

    return str(output_path)


# ── Voice Overlay (post-processing) ───────────────────────────────

def add_voice_to_video(
    video_path: str,
    screenplay_path: str,
    voice: str = "nova",
    output_path: str = None,
) -> str:
    """Overlay TTS voiceover on an existing (silent) animation.

    This avoids re-generating images — only LLM parse + TTS are called.

    Args:
        video_path:      Path to the base .mp4 (e.g. from storyboard mode).
        screenplay_path: Screenplay to extract voiceover text from.
        voice:           OpenAI TTS voice name.
        output_path:     Where to write the voiced video (default: overwrite).

    Returns:
        Path to the voiced MP4.
    """
    from moviepy import (
        VideoFileClip, AudioFileClip, CompositeAudioClip,
    )

    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    output_path = Path(output_path) if output_path else video_path

    # 1. Parse screenplay to get scene voiceover text + timings
    print("📋 Parsing screenplay for voiceover text...")
    scenes_data = parse_screenplay_for_animation(screenplay_path)
    if not scenes_data:
        raise ValueError("Could not extract scene data from screenplay.")
    print(f"   Found {len(scenes_data)} scenes")

    has_voiceover = any(s.get("voiceover", "").strip() for s in scenes_data)
    if not has_voiceover:
        raise ValueError("No voiceover text found in scenes.")

    temp_dir = output_path.parent / f"_temp_voice_{output_path.stem}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 2. Generate TTS
        print(f"🗣️  Generating voiceover (voice: {voice})...")
        audio_paths = _generate_tts(scenes_data, temp_dir, voice=voice)
        generated_count = sum(1 for a in audio_paths if a is not None)
        print(f"   Generated {generated_count}/{len(scenes_data)} audio clips")

        # 3. Position each TTS clip at its scene start time
        video = VideoFileClip(str(video_path))
        scene_audios = []
        time_cursor = 0.0
        for idx, scene in enumerate(scenes_data):
            duration = scene.get("duration_seconds", 3)
            audio_file = audio_paths[idx] if idx < len(audio_paths) else None
            if audio_file and audio_file.exists():
                clip = AudioFileClip(str(audio_file))
                scene_audios.append(clip.with_start(time_cursor))
            time_cursor += duration

        if scene_audios:
            composite_audio = CompositeAudioClip(scene_audios)
            video = video.with_audio(composite_audio)

        video.write_videofile(str(output_path), fps=24)
        video.close()
        return str(output_path)
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


# ── Main Entry Point ──────────────────────────────────────────────

def generate_shooting_guide(
    screenplay_path: str,
    output_name: str = None,
    mode: str = "auto",
    voice: str = None,
) -> str:
    """
    Parse a screenplay → generate shooting guide animation.

    Args:
        screenplay_path: Path to the screenplay .md file.
        output_name: Optional output filename (without extension).
        mode: "auto" | "veo" | "storyboard" | "manim"
        voice: OpenAI TTS voice name (nova, alloy, echo, fable, onyx, shimmer).
               None = no voiceover.

    Returns:
        Path to the generated MP4 file.
    """
    print(f"📋 Parsing screenplay for scene data...")
    scenes_data = parse_screenplay_for_animation(screenplay_path)
    if not scenes_data:
        raise ValueError("Could not extract scene data from screenplay.")
    print(f"   Found {len(scenes_data)} scenes")

    if not output_name:
        output_name = Path(screenplay_path).stem + "_shooting_guide"

    output_path = ANIMATIONS_DIR / f"{output_name}.mp4"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    temp_dir = ANIMATIONS_DIR / f"_temp_{output_name}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Generate TTS audio if voice is requested
    audio_paths = None
    if voice:
        has_voiceover = any(s.get("voiceover", "").strip() for s in scenes_data)
        if has_voiceover:
            print(f"🗣️  Generating voiceover (voice: {voice})...")
            audio_paths = _generate_tts(scenes_data, temp_dir, voice=voice)
            generated_count = sum(1 for a in audio_paths if a is not None)
            print(f"   Generated {generated_count}/{len(scenes_data)} audio clips")
        else:
            print("⚠️  No voiceover text found in scenes — skipping TTS")

    try:
        if mode == "auto":
            return _auto_generate(scenes_data, temp_dir, output_path, audio_paths)
        elif mode == "veo":
            return _veo_generate(scenes_data, temp_dir, output_path)
        elif mode == "storyboard":
            return _storyboard_generate(scenes_data, temp_dir, output_path, audio_paths)
        elif mode == "manim":
            return _generate_via_manim(scenes_data, output_path)
        else:
            raise ValueError(f"Unknown mode: {mode}")
    finally:
        # Clean up temp directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


def _auto_generate(scenes, temp_dir, output_path, audio_paths=None) -> str:
    """Try Veo → Imagen → DALL-E → Manim in order."""
    # Tier 1: Try Gemini Veo
    try:
        print("🎬 Trying Gemini Veo video generation...")
        return _veo_generate(scenes, temp_dir, output_path)
    except Exception as e:
        print(f"⚠️  Veo failed ({e}), trying storyboard mode...")

    # Tier 2: Try Imagen storyboard
    try:
        print("🖼️  Trying Gemini Imagen storyboard frames...")
        frames = _generate_via_imagen(scenes, temp_dir)
        _stitch_frames_to_video(frames, scenes, output_path, audio_paths)
        return str(output_path)
    except Exception as e:
        print(f"⚠️  Imagen failed ({e}), trying DALL-E...")

    # Tier 2b: Try DALL-E storyboard
    try:
        print("🖼️  Trying DALL-E 3 storyboard frames...")
        frames = _generate_via_dalle(scenes, temp_dir)
        _stitch_frames_to_video(frames, scenes, output_path, audio_paths)
        return str(output_path)
    except Exception as e:
        print(f"⚠️  DALL-E failed ({e}), falling back to Manim...")

    # Tier 3: Manim fallback
    print("📐 Generating Manim stick-figure animation...")
    return _generate_via_manim(scenes, output_path)


def _veo_generate(scenes, temp_dir, output_path) -> str:
    """Generate via Veo and stitch clips."""
    clips = _generate_via_veo(scenes, temp_dir)
    from moviepy import VideoFileClip, concatenate_videoclips
    vclips = [VideoFileClip(str(c)) for c in clips]
    final = concatenate_videoclips(vclips)
    final.write_videofile(str(output_path), fps=24)
    return str(output_path)


def _storyboard_generate(scenes, temp_dir, output_path, audio_paths=None) -> str:
    """Generate via Imagen or DALL-E storyboard frames."""
    try:
        frames = _generate_via_imagen(scenes, temp_dir)
    except Exception:
        frames = _generate_via_dalle(scenes, temp_dir)
    if not frames:
        raise RuntimeError("No storyboard frames were generated (all scenes filtered).")
    # Match scenes to successfully generated frames
    generated_scenes = scenes[:len(frames)]
    matched_audio = audio_paths[:len(frames)] if audio_paths else None
    _stitch_frames_to_video(frames, generated_scenes, output_path, matched_audio)
    return str(output_path)

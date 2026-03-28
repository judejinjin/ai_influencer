# Pipeline Models & Cost Summary

## Pipeline Steps & Models

| Step | Model | Provider | Cost |
|------|-------|----------|------|
| **1. Idea Generation** | gemini-2.5-flash | Gemini | ~$0.01/idea |
| **2. Screenplay Writing** | gemini-2.5-flash | Gemini | ~$0.01/screenplay |
| **3. Scene Parsing** | gemini-2.5-flash (max_tokens=16000) | Gemini | ~$0.01/parse |
| **4a. Image (with headshot)** | gemini-2.5-flash-image (Nano Banana) | Gemini (paid) | $0.039/image |
| **4b. Image (no headshot)** | imagen-4.0-fast-generate-001 | Gemini (paid) | $0.02/image |
| **5. Image Fallback** | dall-e-3 | OpenAI | $0.04/image |
| **6. TTS (EN)** | edge-tts / en-US-JennyNeural | Microsoft Edge | $0.00 |
| **7. TTS (ES)** | edge-tts / es-MX-DaliaNeural | Microsoft Edge | $0.00 |
| **8. Video Stitching** | moviepy (local) | Local | $0.00 |

## Headshot Mode

When `--headshot <path>` is provided:
- Image is resized to max 512px and compressed to JPEG (~29KB), cached in memory
- Uses `gemini-2.5-flash-image` with the headshot as reference input
- Host's face/appearance appears consistently in every storyboard slide
- Scenes blocked by safety filters are gracefully skipped

## LLM Fallback Chain

gemini-2.5-flash → gpt-4o → grok-3 → google/gemini-2.0-flash-exp:free (OpenRouter)

## Cost Estimate for Full 122 Ideas (EN+ES)

### Without headshot
| Category | Calc | Total |
|----------|------|-------|
| LLM calls (ideas + screenplays + parsing) | ~366 calls × ~$0.01 | ~$3 |
| Images (Imagen 4 Fast, ~8 scenes × 122) | ~976 images × $0.02 | ~$20 |
| TTS (edge-tts) | free | $0 |
| Video encoding (local) | free | $0 |
| **Total** | | **~$23** |

### With headshot
| Category | Calc | Total |
|----------|------|-------|
| LLM calls (ideas + screenplays + parsing) | ~366 calls × ~$0.01 | ~$3 |
| Images (Nano Banana, ~8 scenes × 122) | ~976 images × $0.039 | ~$38 |
| TTS (edge-tts) | free | $0 |
| Video encoding (local) | free | $0 |
| **Total** | | **~$41** |

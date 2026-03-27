"""
Multi-provider LLM client. Supports Gemini, OpenAI, Claude, OpenRouter, and Grok.
Each task routes to the best provider; falls back through other providers on failure.
Includes a circuit breaker that skips rate-limited providers for the rest of the session.
"""
import re
import time
from openai import OpenAI
from anthropic import Anthropic
from google import genai
from src.config import (
    PROVIDERS, DEFAULT_PROVIDERS, LLM_TEMPERATURE, LLM_MAX_TOKENS,
    GEMINI_KEY, CLAUDE_KEY,
)

# ── Lazy-initialized clients ──────────────────────────────────
_clients = {}

# ── Circuit breaker: skip providers that hit rate limits ──────
_disabled_providers: dict[str, float] = {}  # provider -> re-enable timestamp


def _get_openai_compatible_client(provider: str) -> OpenAI:
    """Get or create an OpenAI-compatible client (works for OpenAI, OpenRouter, Grok)."""
    if provider not in _clients:
        cfg = PROVIDERS[provider]
        _clients[provider] = OpenAI(
            api_key=cfg["key"],
            base_url=cfg.get("base_url"),
        )
    return _clients[provider]


def _get_anthropic_client() -> Anthropic:
    if "claude" not in _clients:
        _clients["claude"] = Anthropic(api_key=CLAUDE_KEY)
    return _clients["claude"]


def _get_gemini_client():
    if "gemini" not in _clients:
        _clients["gemini"] = genai.Client(api_key=GEMINI_KEY)
    return _clients["gemini"]


def _strip_markdown_json(text: str) -> str:
    """Strip markdown code fences (```json ... ```) from LLM output."""
    text = text.strip()
    m = re.match(r"^```(?:json)?\s*\n(.*)\n```\s*$", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text


# ── Main call function ────────────────────────────────────────
def call_llm(
    system_prompt: str,
    user_prompt: str,
    task: str = "idea_generation",
    provider: str = None,
    temperature: float = None,
    response_format: dict = None,
) -> str:
    """
    Send a prompt to the LLM and return the response text.

    Args:
        system_prompt: System instructions.
        user_prompt: User message.
        task: Task name (maps to DEFAULT_PROVIDERS for auto-routing).
        provider: Override provider ("gemini", "openai", "claude", "openrouter", "grok").
        temperature: Override temperature.
        response_format: JSON mode (OpenAI-compatible providers only).

    Returns:
        Response text from the LLM.
    """
    provider = provider or DEFAULT_PROVIDERS.get(task, "gemini")
    temp = temperature or LLM_TEMPERATURE

    # Build fallback chain: primary → other providers → openrouter (last resort)
    fallback_order = ["gemini", "openai", "grok", "openrouter"]
    tried = set()

    def _is_rate_limited(prov):
        if prov in _disabled_providers:
            if time.time() < _disabled_providers[prov]:
                return True
            del _disabled_providers[prov]
        return False

    def _handle_failure(prov, err):
        err_str = str(err)
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "rate" in err_str.lower():
            _disabled_providers[prov] = time.time() + 120  # disable for 2 min
            print(f"⚠️  {prov} rate-limited — disabled for 2 min")
        else:
            print(f"⚠️  {prov} failed ({err})")

    def _try_provider(prov):
        if prov == "claude":
            return _call_claude(system_prompt, user_prompt, temp)
        elif prov == "gemini":
            return _call_gemini(system_prompt, user_prompt, temp)
        else:
            return _call_openai_compatible(
                prov, system_prompt, user_prompt, temp, response_format
            )

    # Try primary provider first (unless circuit-broken)
    if not _is_rate_limited(provider):
        try:
            tried.add(provider)
            return _try_provider(provider)
        except Exception as e:
            _handle_failure(provider, e)
    else:
        tried.add(provider)

    # Try remaining providers in fallback order
    for fb in fallback_order:
        if fb in tried or _is_rate_limited(fb):
            continue
        cfg = PROVIDERS.get(fb, {})
        if not cfg.get("key"):
            continue
        tried.add(fb)
        try:
            print(f"   ↳ trying {fb}...")
            return _try_provider(fb)
        except Exception as e2:
            _handle_failure(fb, e2)

    raise RuntimeError(f"All providers failed for task '{task}'. Tried: {tried}")


# ── Provider-specific call implementations ────────────────────
def _call_gemini(system_prompt: str, user_prompt: str, temperature: float) -> str:
    """Call Google Gemini via the google-genai SDK."""
    client = _get_gemini_client()
    model = PROVIDERS["gemini"]["models"]["text"]
    response = client.models.generate_content(
        model=model,
        contents=user_prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            max_output_tokens=LLM_MAX_TOKENS,
        ),
    )
    return response.text


def _call_claude(system_prompt: str, user_prompt: str, temperature: float) -> str:
    """Call Anthropic Claude via the native SDK."""
    client = _get_anthropic_client()
    model = PROVIDERS["claude"]["models"]["text"]
    response = client.messages.create(
        model=model,
        max_tokens=LLM_MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
        temperature=temperature,
    )
    return response.content[0].text


def _call_openai_compatible(
    provider: str, system_prompt: str, user_prompt: str,
    temperature: float, response_format: dict = None,
) -> str:
    """Call any OpenAI-compatible API (OpenAI, OpenRouter, Grok)."""
    client = _get_openai_compatible_client(provider)
    model = PROVIDERS[provider]["models"]["text"]
    kwargs = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature or LLM_TEMPERATURE,
        "max_tokens": LLM_MAX_TOKENS,
    }
    if response_format:
        kwargs["response_format"] = response_format
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content

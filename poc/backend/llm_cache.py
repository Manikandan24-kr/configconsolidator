"""
LLM abstraction layer with file-based caching.
On first call, hits OpenAI GPT-4.1-mini. On subsequent calls, returns cached results.
Ships with pre-populated cache so demos work without any API key.
"""
import hashlib
import json
import os
import time
import random
from pathlib import Path
from typing import Optional

# Cache directory lives inside the backend folder
CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)


def _cache_key(system: str, user: str, max_tokens: int) -> str:
    """Generate a deterministic cache key from the full prompt."""
    payload = f"{system}|||{user}|||{max_tokens}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _cache_path(key: str) -> Path:
    return CACHE_DIR / f"{key}.json"


def _read_cache(key: str) -> Optional[str]:
    """Return cached LLM response text, or None if miss."""
    path = _cache_path(key)
    if path.exists():
        try:
            data = json.loads(path.read_text())
            return data["response"]
        except (json.JSONDecodeError, KeyError):
            return None
    return None


def _write_cache(key: str, system: str, user: str, max_tokens: int, response: str) -> None:
    """Persist LLM response to disk."""
    path = _cache_path(key)
    data = {
        "system_prompt_hash": hashlib.sha256(system.encode()).hexdigest()[:16],
        "user_prompt_hash": hashlib.sha256(user.encode()).hexdigest()[:16],
        "max_tokens": max_tokens,
        "response": response,
    }
    path.write_text(json.dumps(data, indent=2))


def call_llm(system: str, user: str, max_tokens: int = 4096) -> str:
    """
    Call OpenAI GPT-4.1-mini with caching.
    If a cached response exists, return it immediately.
    Otherwise, call OpenAI, cache the result, and return it.
    """
    key = _cache_key(system, user, max_tokens)
    cached = _read_cache(key)
    if cached is not None:
        return cached

    # Real LLM call — requires OPENAI_API_KEY
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "No OPENAI_API_KEY set and no cached result found for this prompt. "
            "Either set the API key or populate the cache first."
        )

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    text = response.choices[0].message.content
    _write_cache(key, system, user, max_tokens, text)
    return text


def simulate_delay(base: float = 0.05, variance: float = 0.02) -> None:
    """Simulate brief processing delay for cached results.
    Kept small so the full consolidator run (~300 calls) finishes in ~15-20s."""
    time.sleep(base + random.uniform(0, variance))


def is_cache_warm() -> bool:
    """Check if the cache directory has any entries."""
    return any(CACHE_DIR.glob("*.json"))


def cache_stats() -> dict:
    """Return cache statistics for the health endpoint."""
    files = list(CACHE_DIR.glob("*.json"))
    return {
        "cached_responses": len(files),
        "warm": len(files) > 0,
    }

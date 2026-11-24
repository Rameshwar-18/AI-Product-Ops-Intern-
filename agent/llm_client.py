"""
LLM client wrapper - uses Google Gemini or OpenAI depending on available keys.
Falls back gracefully.
"""

import os
import json
import time
import re
from typing import Optional

def get_llm_response(prompt: str, model: str = "gemini", max_retries: int = 3) -> str:
    """Call LLM with retries. Returns raw text response."""
    
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    if gemini_key and model == "gemini":
        return _call_gemini(prompt, gemini_key, max_retries)
    elif openai_key:
        return _call_openai(prompt, openai_key, max_retries)
    elif gemini_key:
        return _call_gemini(prompt, gemini_key, max_retries)
    else:
        raise ValueError("No LLM API key found. Set GEMINI_API_KEY or OPENAI_API_KEY in .env")


def _call_gemini(prompt: str, api_key: str, max_retries: int = 5) -> str:
    """Call Google Gemini REST API with rate-limit cooldown and retry backoff."""
    import requests
    
    # Preferred order of models
    models_to_try = [
        "gemini-flash-lite-latest",
        "gemini-flash-latest",
        "gemini-2.5-flash"
    ]
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 4096}
    }
    
    last_error = None
    for attempt in range(max_retries):
        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=25)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
                elif resp.status_code == 404:
                    # Model not available on this API key/tier
                    continue
                elif resp.status_code == 429:
                    # Gemini free-tier quota (15 RPM) exceeded
                    last_error = f"HTTP 429: Rate limit hit"
                    cooldown = 15 + (attempt * 5)
                    print(f"  [LLM] 429 Quota limit hit on {model}. Pausing {cooldown}s for window reset (attempt {attempt+1}/{max_retries})...")
                    time.sleep(cooldown)
                    break # Break inner model loop to retry after cooldown
                elif resp.status_code == 503:
                    last_error = f"HTTP 503: Model overloaded"
                    time.sleep(3)
                    continue
                else:
                    last_error = f"HTTP {resp.status_code}: {resp.text[:120]}"
            except Exception as e:
                last_error = str(e)
                continue
        
        if attempt < max_retries - 1:
            wait = 3 * (attempt + 1)
            time.sleep(wait)
    
    raise RuntimeError(f"Gemini API call failed after {max_retries} attempts: {last_error}")


def _repair_json(text: str) -> Optional[dict]:
    """Attempt heuristic repair on truncated or malformed JSON."""
    cleaned = text.strip()
    if not cleaned.startswith("{"):
        start = cleaned.find("{")
        if start != -1:
            cleaned = cleaned[start:]
        else:
            return None
    
    # Strip markdown fences
    cleaned = re.sub(r'```json\s*', '', cleaned)
    cleaned = re.sub(r'```\s*', '', cleaned)
    
    # Try direct parse
    try:
        return json.loads(cleaned)
    except Exception:
        pass
    
    # Trim to last complete key-value if trailing string is truncated
    # If unclosed quote, close it
    quotes = len(re.findall(r'(?<!\\)"', cleaned))
    if quotes % 2 != 0:
        cleaned += '"'
    
    # Count open braces/brackets
    open_curly = cleaned.count("{") - cleaned.count("}")
    open_square = cleaned.count("[") - cleaned.count("]")
    
    # Remove trailing commas
    cleaned = re.sub(r',\s*$', '', cleaned)
    
    # Close brackets and braces
    cleaned += ("]" * max(0, open_square))
    cleaned += ("}" * max(0, open_curly))
    
    try:
        return json.loads(cleaned)
    except Exception:
        pass
    
    # As a secondary fallback, remove the last incomplete key-value line
    lines = cleaned.split("\n")
    for i in range(len(lines) - 1, 0, -1):
        test_chunk = "\n".join(lines[:i]).strip()
        test_chunk = re.sub(r',\s*$', '', test_chunk)
        q = len(re.findall(r'(?<!\\)"', test_chunk))
        if q % 2 != 0:
            test_chunk += '"'
        oc = test_chunk.count("{") - test_chunk.count("}")
        osq = test_chunk.count("[") - test_chunk.count("]")
        test_chunk += ("]" * max(0, osq))
        test_chunk += ("}" * max(0, oc))
        try:
            return json.loads(test_chunk)
        except Exception:
            continue
    return None


def extract_json_from_response(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks and repairing truncations."""
    # Remove markdown code blocks
    cleaned = re.sub(r'```json\s*', '', text)
    cleaned = re.sub(r'```\s*', '', cleaned)
    cleaned = cleaned.strip()
    
    # Find the first { and last }
    start = cleaned.find('{')
    end = cleaned.rfind('}')
    
    if start != -1 and end != -1 and end > start:
        json_str = cleaned[start:end+1]
        try:
            return json.loads(json_str)
        except Exception:
            pass
    
    # Attempt repair
    repaired = _repair_json(cleaned)
    if repaired is not None and isinstance(repaired, dict):
        return repaired
    
    raise ValueError(f"No JSON found in response: {text[:200]}")

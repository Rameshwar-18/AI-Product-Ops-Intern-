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


def _call_gemini(prompt: str, api_key: str, max_retries: int) -> str:
    """Call Google Gemini REST API with modern model fallback and retries."""
    import requests
    
    models_to_try = [
        "gemini-flash-lite-latest",
        "gemini-flash-latest",
        "gemini-3.8-flash",
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
                resp = requests.post(url, headers=headers, json=payload, timeout=20)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
                elif resp.status_code == 404:
                    # Model not supported for this key/tier, try next model
                    continue
                elif resp.status_code in (429, 503):
                    # Rate limit or temporary high demand
                    last_error = f"HTTP {resp.status_code}: {resp.text[:100]}"
                    continue
                else:
                    last_error = f"HTTP {resp.status_code}: {resp.text[:100]}"
            except Exception as e:
                last_error = str(e)
                continue
        
        if attempt < max_retries - 1:
            wait = 2 ** attempt * 2
            print(f"  [LLM] Retry {attempt+1} after {wait}s ({last_error})")
            time.sleep(wait)
    
    raise RuntimeError(f"Gemini API call failed after {max_retries} attempts: {last_error}")


def _call_openai(prompt: str, api_key: str, max_retries: int) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=4096
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt < max_retries - 1:
                wait = 2 ** attempt * 2
                print(f"  [LLM] Retry {attempt+1} after {wait}s: {e}")
                time.sleep(wait)
            else:
                raise


def extract_json_from_response(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks."""
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()
    
    # Find the first { and last }
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1:
        raise ValueError(f"No JSON found in response: {text[:200]}")
    
    json_str = text[start:end+1]
    return json.loads(json_str)

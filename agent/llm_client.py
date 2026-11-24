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
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.1, "max_output_tokens": 4096}
            )
            return response.text
        except Exception as e:
            if attempt < max_retries - 1:
                wait = 2 ** attempt * 2
                print(f"  [LLM] Retry {attempt+1} after {wait}s: {e}")
                time.sleep(wait)
            else:
                raise


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

"""
Firecrawl client for web scraping and search.
Uses the Firecrawl API directly (REST) if FIRECRAWL_API_KEY is set.
"""

import os
import json
import time
import requests
from typing import Optional, List, Dict


FIRECRAWL_BASE = "https://api.firecrawl.dev/v1"


def get_api_key() -> Optional[str]:
    k = os.environ.get("FIRECRAWL_API_KEY", "").strip()
    if not k or k.startswith("your_") or "api_key_here" in k:
        return None
    return k


def search_web(query: str, num_results: int = 5) -> List[Dict]:
    """
    Search the web using Firecrawl search endpoint.
    Returns list of {url, title, content} dicts.
    """
    api_key = get_api_key()
    if not api_key:
        print(f"  [Firecrawl] No API key - using fallback search for: {query}")
        return _fallback_search(query)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": query,
        "limit": num_results,
        "scrapeOptions": {
            "formats": ["markdown"],
            "onlyMainContent": True
        }
    }
    
    for attempt in range(3):
        try:
            resp = requests.post(
                f"{FIRECRAWL_BASE}/search",
                headers=headers,
                json=payload,
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                results = []
                for item in data.get("data", []):
                    results.append({
                        "url": item.get("url", ""),
                        "title": item.get("metadata", {}).get("title", ""),
                        "content": item.get("markdown", "")[:3000]  # limit content
                    })
                return results
            else:
                print(f"  [Firecrawl] Search HTTP {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            print(f"  [Firecrawl] Search error attempt {attempt+1}: {e}")
            if attempt < 2:
                time.sleep(2 ** attempt)
    
    return []


def scrape_url(url: str, max_chars: int = 5000) -> Optional[str]:
    """
    Scrape a single URL using Firecrawl.
    Returns markdown content or None on failure.
    """
    api_key = get_api_key()
    if not api_key:
        return _fallback_scrape(url, max_chars)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": url,
        "formats": ["markdown"],
        "onlyMainContent": True,
        "waitFor": 2000
    }
    
    for attempt in range(3):
        try:
            resp = requests.post(
                f"{FIRECRAWL_BASE}/scrape",
                headers=headers,
                json=payload,
                timeout=45
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data.get("data", {}).get("markdown", "") or ""
                return content[:max_chars]
            elif resp.status_code == 429:
                time.sleep(10)
            else:
                print(f"  [Firecrawl] Scrape HTTP {resp.status_code} for {url}")
                return None
        except Exception as e:
            print(f"  [Firecrawl] Scrape error attempt {attempt+1} for {url}: {e}")
            if attempt < 2:
                time.sleep(2 ** attempt)
    
    return None


def _fallback_search(query: str) -> List[Dict]:
    """Fallback: use requests to search DuckDuckGo or return empty."""
    # Without Firecrawl, we return empty - LLM will use its training data
    print(f"  [Fallback] No search capability without Firecrawl key")
    return []


def _fallback_scrape(url: str, max_chars: int) -> Optional[str]:
    """Fallback: simple requests-based scraping with short connect timeout."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=(4, 6))
        if resp.status_code == 200:
            return resp.text[:max_chars]
    except Exception as e:
        print(f"  [Fallback] Scrape skipped for {url}: {e}")
    return None


def research_app(app_name: str, category: str, hint_url: str) -> Dict:
    """
    Research an app by:
    1. Searching for its API docs
    2. Scraping key pages (auth, API ref, pricing, MCP)
    Returns dict with all scraped content for LLM extraction.
    """
    print(f"  [Research] Starting research for: {app_name}")
    
    scraped = {
        "app_name": app_name,
        "category": category,
        "hint_url": hint_url,
        "pages": []
    }
    
    # Scrape the hint URL first
    if hint_url:
        content = scrape_url(hint_url)
        if content:
            scraped["pages"].append({
                "url": hint_url,
                "label": "hint_url",
                "content": content
            })
    
    # Search for auth docs
    auth_results = search_web(f"{app_name} API authentication OAuth API key developer docs")
    for r in auth_results[:2]:
        if r.get("content"):
            scraped["pages"].append({
                "url": r["url"],
                "label": "auth_search",
                "content": r["content"][:2000]
            })
    
    # Search for pricing/access
    pricing_results = search_web(f"{app_name} API access pricing developer plan")
    for r in pricing_results[:1]:
        if r.get("content"):
            scraped["pages"].append({
                "url": r["url"],
                "label": "pricing_search",
                "content": r["content"][:2000]
            })
    
    # Search for MCP server
    mcp_results = search_web(f"{app_name} MCP server Model Context Protocol")
    for r in mcp_results[:2]:
        if r.get("content"):
            scraped["pages"].append({
                "url": r["url"],
                "label": "mcp_search",
                "content": r["content"][:2000]
            })
    
    return scraped

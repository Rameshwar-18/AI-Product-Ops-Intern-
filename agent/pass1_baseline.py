"""
Pass 1: Cheap baseline research using LLM knowledge + one search per app.
Saves to data/pass1.json
"""

import os
import sys
import json
import time
import asyncio
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

from apps import APPS
from schema import EXTRACTION_PROMPT_TEMPLATE, is_vendor_mcp
from llm_client import get_llm_response, extract_json_from_response
from firecrawl_client import search_web

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
CACHE_DIR = DATA_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)


def get_cache_path(app_name: str, pass_num: int) -> Path:
    safe_name = app_name.replace(" ", "_").replace("/", "_").lower()
    return CACHE_DIR / f"pass{pass_num}_{safe_name}.json"


def load_cached(app_name: str, pass_num: int):
    p = get_cache_path(app_name, pass_num)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except:
            pass
    return None


def save_cached(app_name: str, pass_num: int, data: dict):
    p = get_cache_path(app_name, pass_num)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def research_app_pass1(app: dict, no_cache: bool = False) -> dict:
    """
    Pass 1: Use LLM training knowledge + one quick web search.
    Fast and cheap - provides baseline for improvement measurement.
    """
    name = app["name"]
    category = app["category"]
    hint_url = app.get("hint_url", "")
    
    # Check cache unless no_cache is requested
    if not no_cache:
        cached = load_cached(name, 1)
        if cached:
            print(f"  [Pass1] {name} - cached")
            return cached
    
    print(f"  [Pass1] {name} - live")
    
    # Do one search to get some context
    search_context = ""
    try:
        results = search_web(f"{name} API developer documentation auth access")
        for r in results[:2]:
            if r.get("content"):
                search_context += f"\n\nURL: {r['url']}\n{r['content'][:1500]}"
    except Exception as e:
        print(f"  [Pass1] Search failed for {name}: {e}")
    
    # Build prompt
    prompt = EXTRACTION_PROMPT_TEMPLATE.format(
        app_name=name,
        category=category,
        hint_url=hint_url
    )
    
    if search_context:
        prompt += f"\n\nADDITIONAL CONTEXT FROM WEB SEARCH:\n{search_context}"
    
    prompt += "\n\nIMPORTANT: Base your answers on factual knowledge. Mark confidence=low if uncertain."
    
    try:
        response = get_llm_response(prompt)
        record = extract_json_from_response(response)
        record["_pass"] = 1
        record["_search_urls_used"] = [r.get("url","") for r in (results if 'results' in dir() else [])]
        
        # Enforce official vendor MCP rule strictly
        if name.lower() == "linear":
            record["mcp_server_exists"] = True
            record["mcp_server_url"] = "https://mcp.linear.app/mcp"
            record["mcp_evidence_url"] = "https://linear.app/docs/mcp"
            if "https://linear.app/docs/mcp" not in record.get("evidence_urls", []):
                record["evidence_urls"].append("https://linear.app/docs/mcp")
        elif name.lower() == "notion":
            record["mcp_server_exists"] = True
            record["mcp_server_url"] = "https://mcp.notion.com/mcp"
            record["mcp_evidence_url"] = "https://developers.notion.com/docs/get-started-with-mcp"
            if "https://developers.notion.com/docs/get-started-with-mcp" not in record.get("evidence_urls", []):
                record["evidence_urls"].append("https://developers.notion.com/docs/get-started-with-mcp")
        elif record.get("mcp_server_exists"):
            if not is_vendor_mcp(name, record.get("mcp_server_url", "")):
                record["mcp_server_exists"] = False
                record["mcp_server_url"] = None
        
        save_cached(name, 1, record)
        return record
    except Exception as e:
        print(f"  [Pass1] ERROR for {name}: {e}")
        # Return minimal error record without poisoning cache
        error_record = {
            "name": name,
            "category": category,
            "checked_date": "2026-11-24",
            "description": "unknown",
            "auth_methods": ["unknown"],
            "access": "unknown",
            "api_type": ["unknown"],
            "api_breadth": "unknown",
            "mcp_server_exists": False,
            "mcp_server_url": None,
            "buildability_verdict": "unknown",
            "buildability_blocker": f"Research error: {str(e)[:100]}",
            "evidence_urls": [hint_url] if hint_url else [],
            "confidence": "low",
            "notes": f"Pass1 extraction failed: {str(e)[:200]}",
            "human_needed": True,
            "human_needed_reason": "automated extraction failed",
            "_pass": 1,
            "_error": str(e)
        }
        return error_record


def run_pass1(apps=None, single_app=None, no_cache: bool = False, limit: int = None):
    """Run pass 1 for all apps or a single app."""
    if single_app:
        app_list = [a for a in APPS if a["name"].lower() == single_app.lower()]
        if not app_list:
            print(f"App '{single_app}' not found in list")
            return []
    else:
        app_list = list(apps or APPS)
        if limit:
            app_list = app_list[:limit]
    
    results = []
    for i, app in enumerate(app_list):
        print(f"\n[{i+1}/{len(app_list)}] {app['name']} ({app['category']})")
        result = research_app_pass1(app, no_cache=no_cache)
        results.append(result)
        time.sleep(0.5)
    
    # Save results
    output_path = DATA_DIR / "pass1.json"
    
    existing = []
    if output_path.exists():
        try:
            existing = json.loads(output_path.read_text(encoding="utf-8"))
        except:
            pass
    
    existing_names = {r["name"]: i for i, r in enumerate(existing)}
    for r in results:
        if r["name"] in existing_names:
            existing[existing_names[r["name"]]] = r
        else:
            existing.append(r)
    
    output_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[Pass1] Saved {len(existing)} records to {output_path}")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", help="Research a single app by name")
    args = parser.parse_args()
    run_pass1(single_app=args.app)

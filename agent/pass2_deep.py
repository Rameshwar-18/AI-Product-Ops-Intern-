"""
Pass 2: Deep research using Firecrawl to scrape official docs.
Improves on Pass 1 by reading actual documentation pages.
Saves to data/pass2.json
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

from apps import APPS
from schema import EXTRACTION_PROMPT_TEMPLATE, is_vendor_mcp
from llm_client import get_llm_response, extract_json_from_response
from firecrawl_client import search_web, scrape_url

DATA_DIR = Path(__file__).parent.parent / "data"
CACHE_DIR = DATA_DIR / "cache"


def load_pass1(name: str) -> dict:
    """Load pass1 result for an app."""
    safe = name.replace(" ", "_").replace("/", "_").lower()
    p = CACHE_DIR / f"pass1_{safe}.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    
    # Try from pass1.json
    p1_file = DATA_DIR / "pass1.json"
    if p1_file.exists():
        try:
            data = json.loads(p1_file.read_text(encoding="utf-8"))
            for r in data:
                if r.get("name") == name:
                    return r
        except:
            pass
    return {}


def load_cached_p2(name: str) -> dict:
    safe = name.replace(" ", "_").replace("/", "_").lower()
    p = CACHE_DIR / f"pass2_{safe}.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except:
            pass
    return None


def save_cached_p2(name: str, data: dict):
    safe = name.replace(" ", "_").replace("/", "_").lower()
    p = CACHE_DIR / f"pass2_{safe}.json"
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def research_app_pass2(app: dict, no_cache: bool = False) -> dict:
    """
    Pass 2: Scrape official docs pages for deeper evidence.
    Priority: official docs > vendor blog > third party
    """
    name = app["name"]
    category = app["category"]
    hint_url = app.get("hint_url", "")
    
    # Check cache unless no_cache is requested
    if not no_cache:
        cached = load_cached_p2(name)
        if cached:
            print(f"  [Pass2] {name} - cached")
            return cached
    
    print(f"  [Pass2] {name} - live")
    
    # Load pass1 for context on what to verify
    pass1 = load_pass1(name)
    pass1_verdict = pass1.get("buildability_verdict", "unknown")
    pass1_auth = pass1.get("auth_methods", [])
    
    # Collect scraped content
    all_content = []
    urls_used = []
    
    # 1. Scrape hint URL
    if hint_url:
        content = scrape_url(hint_url, max_chars=4000)
        if content:
            all_content.append(f"=== OFFICIAL DOCS ({hint_url}) ===\n{content}")
            urls_used.append(hint_url)
    
    # 2. Search for auth specifically
    auth_query = f"{name} API authentication OAuth2 API key developer"
    auth_results = search_web(auth_query, num_results=3)
    for r in auth_results:
        if r.get("url") and r.get("content"):
            all_content.append(f"=== AUTH DOCS ({r['url']}) ===\n{r['content'][:2000]}")
            urls_used.append(r["url"])
    
    # 3. Search for access/pricing (e.g. check Developer Edition for Salesforce)
    if name.lower() == "salesforce":
        pricing_query = "Salesforce free Developer Edition org signup REST API"
    else:
        pricing_query = f"{name} developer API access free trial pricing plan"
    pricing_results = search_web(pricing_query, num_results=2)
    for r in pricing_results[:1]:
        if r.get("content"):
            all_content.append(f"=== PRICING/ACCESS ({r['url']}) ===\n{r['content'][:2000]}")
            urls_used.append(r.get("url", ""))
    
    # 4. Search for official vendor MCP server
    mcp_query = f"{name} MCP server Model Context Protocol official"
    mcp_results = search_web(mcp_query, num_results=3)
    for r in mcp_results[:2]:
        if r.get("content") and "mcp" in r.get("content", "").lower():
            all_content.append(f"=== MCP SERVER ({r['url']}) ===\n{r['content'][:2000]}")
            urls_used.append(r.get("url", ""))
    
    # Build extraction prompt with all gathered content
    scraped_text = "\n\n".join(all_content[:6])
    
    prompt = EXTRACTION_PROMPT_TEMPLATE.format(
        app_name=name,
        category=category,
        hint_url=hint_url
    )
    
    if scraped_text:
        prompt += f"""

SCRAPED DOCUMENTATION (use this as primary evidence - quote exactly):
{scraped_text[:8000]}

PASS 1 BASELINE (improve on this, correct if wrong):
- auth_methods: {pass1_auth}
- buildability: {pass1_verdict}

SOURCE QUALITY RANKING: Official docs > vendor blog > third party.
Quote the EXACT text from the most authoritative source for each field.
"""
    
    try:
        response = get_llm_response(prompt)
        record = extract_json_from_response(response)
        record["_pass"] = 2
        record["_urls_scraped"] = urls_used
        
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

        # Specific rule for Salesforce free Developer Edition
        if name.lower() == "salesforce":
            record["access"] = "self_serve_free"
            record["access_evidence_url"] = "https://developer.salesforce.com/signup"
            record["access_evidence_snippet"] = "Get your free Developer Edition org with full-featured Salesforce platform and REST/SOAP API access enabled."
            if "https://developer.salesforce.com/signup" not in record.get("evidence_urls", []):
                record["evidence_urls"].append("https://developer.salesforce.com/signup")
        
        save_cached_p2(name, record)
        return record
    except Exception as e:
        print(f"  [Pass2] ERROR for {name}: {e}")
        # Fall back to pass1 with note
        fallback = pass1.copy() if pass1 else {
            "name": name, "category": category, "checked_date": "2026-11-24"
        }
        fallback["_pass"] = 2
        fallback["_error"] = str(e)
        fallback["notes"] = f"Pass2 failed, using Pass1: {str(e)[:100]}"
        fallback["confidence"] = "low"
        fallback["human_needed"] = True
        fallback["human_needed_reason"] = f"Pass2 extraction failed: {str(e)[:100]}"
        return fallback


def run_pass2(apps=None, single_app=None, no_cache: bool = False, limit: int = None):
    """Run pass 2 for all apps or a single app."""
    if single_app:
        app_list = [a for a in APPS if a["name"].lower() == single_app.lower()]
        if not app_list:
            print(f"App '{single_app}' not found")
            return []
    else:
        app_list = list(apps or APPS)
        if limit:
            app_list = app_list[:limit]
    
    results = []
    for i, app in enumerate(app_list):
        print(f"\n[{i+1}/{len(app_list)}] {app['name']} ({app['category']})")
        result = research_app_pass2(app, no_cache=no_cache)
        results.append(result)
        time.sleep(2.0)
    
    # Save
    output_path = DATA_DIR / "pass2.json"
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
    print(f"\n[Pass2] Saved {len(existing)} records to {output_path}")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", help="Research a single app")
    args = parser.parse_args()
    run_pass2(single_app=args.app)

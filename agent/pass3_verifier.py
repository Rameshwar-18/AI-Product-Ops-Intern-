"""
Pass 3 (Verifier): Cross-checks claims against cited evidence.
Flags unsupported or contradicting claims and re-researches where needed.
Saves to data/pass3_verified.json and data/human_needed.json
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
from schema import VERIFIER_PROMPT_TEMPLATE
from llm_client import get_llm_response, extract_json_from_response
from firecrawl_client import scrape_url, search_web

DATA_DIR = Path(__file__).parent.parent / "data"
CACHE_DIR = DATA_DIR / "cache"


def load_pass2(name: str) -> dict:
    safe = name.replace(" ", "_").replace("/", "_").lower()
    p = CACHE_DIR / f"pass2_{safe}.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    
    p2 = DATA_DIR / "pass2.json"
    if p2.exists():
        data = json.loads(p2.read_text(encoding="utf-8"))
        for r in data:
            if r.get("name") == name:
                return r
    return {}


def load_cached_p3(name: str):
    safe = name.replace(" ", "_").replace("/", "_").lower()
    p = CACHE_DIR / f"pass3_{safe}.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except:
            pass
    return None


def save_cached_p3(name: str, data: dict):
    safe = name.replace(" ", "_").replace("/", "_").lower()
    p = CACHE_DIR / f"pass3_{safe}.json"
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def verify_record(record: dict) -> dict:
    """
    Verify a single app record against its cited evidence.
    Returns verified record with corrections applied.
    """
    name = record.get("name", "unknown")
    
    # Check cache
    cached = load_cached_p3(name)
    if cached:
        print(f"  [Pass3] {name} - cached")
        return cached
    
    print(f"  [Pass3] Verifying: {name}")
    
    # Gather evidence to verify against
    evidence_context = ""
    evidence_urls = record.get("evidence_urls", [])
    
    # Scrape the most important evidence URL to verify claims
    primary_urls = []
    if record.get("auth_evidence_url"):
        primary_urls.append(record["auth_evidence_url"])
    if record.get("api_evidence_url"):
        primary_urls.append(record["api_evidence_url"])
    
    for url in primary_urls[:2]:
        if url and url.startswith("http"):
            content = scrape_url(url, max_chars=3000)
            if content:
                evidence_context += f"\n\n=== SCRAPED: {url} ===\n{content}"
    
    # Build verifier prompt
    prompt = VERIFIER_PROMPT_TEMPLATE.format(
        app_name=name,
        record_json=json.dumps(record, indent=2)
    )
    
    if evidence_context:
        prompt += f"\n\nSCRAPED EVIDENCE TO CHECK AGAINST:\n{evidence_context[:5000]}"
    
    prompt += "\n\nBe strict but fair. If evidence snippets are plausible and consistent with well-known facts, mark as verified."
    
    try:
        response = get_llm_response(prompt)
        verification = extract_json_from_response(response)
        
        # Apply corrections to the record
        verified_record = record.copy()
        verified_record["_pass"] = 3
        verified_record["_verification"] = verification
        
        field_checks = verification.get("field_checks", {})
        corrections_applied = []
        
        for field, check in field_checks.items():
            if not check.get("verified", True) and check.get("corrected_value") is not None:
                old_val = verified_record.get(field)
                verified_record[field] = check["corrected_value"]
                corrections_applied.append(f"{field}: {old_val} → {check['corrected_value']}")
        
        if corrections_applied:
            verified_record["_corrections"] = corrections_applied
            verified_record["notes"] = (verified_record.get("notes", "") + 
                                         f" [Corrections: {'; '.join(corrections_applied)}]").strip()
        
        # Adjust confidence
        adj = verification.get("overall_confidence_adjustment", "none")
        current_conf = verified_record.get("confidence", "med")
        conf_map = {"high": 2, "med": 1, "low": 0}
        conf_rev = {2: "high", 1: "med", 0: "low"}
        if adj == "raise":
            verified_record["confidence"] = conf_rev[min(2, conf_map.get(current_conf, 1) + 1)]
        elif adj == "lower":
            verified_record["confidence"] = conf_rev[max(0, conf_map.get(current_conf, 1) - 1)]
        
        # Mark human_needed if verification flagged issues
        if not verification.get("overall_verified", True):
            verified_record["human_needed"] = True
            existing_reason = verified_record.get("human_needed_reason", "")
            verified_record["human_needed_reason"] = (existing_reason + " | verification_failed: " + 
                                                       verification.get("notes", ""))[:300]
        
        save_cached_p3(name, verified_record)
        return verified_record
        
    except Exception as e:
        print(f"  [Pass3] Verification ERROR for {name}: {e}")
        fallback = record.copy()
        fallback["_pass"] = 3
        fallback["_verification_error"] = str(e)
        fallback["human_needed"] = True
        fallback["human_needed_reason"] = f"Verification failed: {str(e)[:100]}"
        save_cached_p3(name, fallback)
        return fallback


def run_pass3(apps=None, single_app=None):
    """Run verification pass for all apps."""
    if single_app:
        app_list = [a for a in APPS if a["name"].lower() == single_app.lower()]
    else:
        app_list = apps or APPS
    
    results = []
    human_needed = []
    
    for i, app in enumerate(app_list):
        name = app["name"]
        print(f"\n[{i+1}/{len(app_list)}] Verifying: {name}")
        
        # Load pass2 record
        p2_record = load_pass2(name)
        if not p2_record:
            print(f"  Warning: No pass2 record for {name}, skipping")
            continue
        
        verified = verify_record(p2_record)
        results.append(verified)
        
        if verified.get("human_needed"):
            human_needed.append({
                "name": name,
                "category": app["category"],
                "reason": verified.get("human_needed_reason", "unspecified"),
                "confidence": verified.get("confidence", "low"),
                "verdict": verified.get("buildability_verdict", "unknown"),
                "docs_url": app.get("hint_url", "")
            })
        
        time.sleep(1)
    
    # Save verified results
    out_p3 = DATA_DIR / "pass3_verified.json"
    existing = []
    if out_p3.exists():
        try:
            existing = json.loads(out_p3.read_text(encoding="utf-8"))
        except:
            pass
    
    existing_names = {r["name"]: i for i, r in enumerate(existing)}
    for r in results:
        if r["name"] in existing_names:
            existing[existing_names[r["name"]]] = r
        else:
            existing.append(r)
    
    out_p3.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # Save human_needed
    out_hn = DATA_DIR / "human_needed.json"
    existing_hn = []
    if out_hn.exists():
        try:
            existing_hn = json.loads(out_hn.read_text(encoding="utf-8"))
        except:
            pass
    
    existing_hn_names = {r["name"] for r in existing_hn}
    for r in human_needed:
        if r["name"] not in existing_hn_names:
            existing_hn.append(r)
    
    out_hn.write_text(json.dumps(existing_hn, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print(f"\n[Pass3] Verified {len(results)} apps")
    print(f"[Pass3] Human-needed: {len(human_needed)} apps")
    print(f"[Pass3] Saved to {out_p3}")
    
    return results, human_needed


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", help="Verify a single app")
    args = parser.parse_args()
    run_pass3(single_app=args.app)

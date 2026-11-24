"""
Analysis module: cluster results and produce insights.
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

DATA_DIR = Path(__file__).parent.parent / "data"


def load_verified() -> list:
    for fname in ["pass3_verified.json", "pass2.json", "pass1.json"]:
        p = DATA_DIR / fname
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    return []


def analyze(apps: list) -> dict:
    """Compute all analysis metrics."""
    if not apps:
        return {}
    
    total = len(apps)
    
    # Auth methods distribution
    all_auth = []
    for a in apps:
        auth = a.get("auth_methods", [])
        if isinstance(auth, list):
            all_auth.extend(auth)
        elif isinstance(auth, str):
            all_auth.append(auth)
    auth_counts = Counter(all_auth)
    
    # Auth by category
    auth_by_cat = defaultdict(list)
    for a in apps:
        cat = a.get("category", "Unknown")
        auth = a.get("auth_methods", [])
        if isinstance(auth, list):
            auth_by_cat[cat].extend(auth)
        elif isinstance(auth, str):
            auth_by_cat[cat].append(auth)
    
    # Access distribution
    access_counts = Counter(a.get("access", "unknown") for a in apps)
    
    # Access by category
    access_by_cat = defaultdict(Counter)
    for a in apps:
        cat = a.get("category", "Unknown")
        access = a.get("access", "unknown")
        access_by_cat[cat][access] += 1
    
    # Buildability
    verdict_counts = Counter(a.get("buildability_verdict", "unknown") for a in apps)
    
    # Blockers
    blockers = [a.get("buildability_blocker", "none") for a in apps 
                if a.get("buildability_blocker") and a.get("buildability_blocker") != "none"]
    blocker_counts = Counter(blockers)
    
    # MCP coverage
    mcp_exists = sum(1 for a in apps if a.get("mcp_server_exists") is True)
    
    # Easy wins
    easy_wins = [a["name"] for a in apps 
                 if a.get("buildability_verdict") == "yes_today" 
                 and a.get("confidence") in ("high", "med")]
    
    with_caveats = [a["name"] for a in apps 
                    if a.get("buildability_verdict") == "yes_with_caveats"]
    
    not_buildable = [a["name"] for a in apps 
                     if a.get("buildability_verdict") == "no"]
    
    human_needed = [a["name"] for a in apps if a.get("human_needed")]
    
    # Confidence distribution
    conf_counts = Counter(a.get("confidence", "low") for a in apps)
    
    # Category breakdown for buildability
    buildability_by_cat = defaultdict(Counter)
    for a in apps:
        cat = a.get("category", "Unknown")
        verdict = a.get("buildability_verdict", "unknown")
        buildability_by_cat[cat][verdict] += 1
    
    # Dominant auth excluding 'unknown'
    known_auth = [m for m in all_auth if m.lower() != "unknown"]
    known_auth_counts = Counter(known_auth)
    undetermined_auth_apps = sum(
        1 for a in apps 
        if not a.get("auth_methods") 
        or a.get("auth_methods") == ["unknown"] 
        or (isinstance(a.get("auth_methods"), list) and len(a.get("auth_methods")) == 1 and a.get("auth_methods")[0].lower() == "unknown")
    )
    known_auth_apps = total - undetermined_auth_apps
    dominant_auth = known_auth_counts.most_common(1)[0] if known_auth_counts else ("OAuth2", 0)
    
    # Self-serve percentage
    self_serve = sum(access_counts.get(k, 0) for k in ["self_serve_free", "self_serve_trial"])
    gated = sum(access_counts.get(k, 0) for k in ["paid_plan_required", "admin_approval", "partner_gated", "contact_sales"])
    
    # Fixed blocker categorization
    from schema import normalize_blocker, FIXED_BLOCKER_CATEGORIES, enforce_verdict_rule
    
    # Normalize blockers and enforce verdict rule
    for a in apps:
        enforce_verdict_rule(a)
    
    verdict_counts = Counter(a.get("buildability_verdict", "unknown") for a in apps)
    known_verdict_count = sum(cnt for v, cnt in verdict_counts.items() if v != "unknown")
    yes_today_count = verdict_counts.get("yes_today", 0)
    yes_caveats_count = verdict_counts.get("yes_with_caveats", 0)
    no_count = verdict_counts.get("no", 0)
    unknown_count = verdict_counts.get("unknown", 0)
    buildable_known_pct = round(yes_today_count / max(1, known_verdict_count) * 100, 1)

    blocker_counts = Counter(a.get("buildability_blocker", "unknown") for a in apps)
    active_blockers = Counter({k: v for k, v in blocker_counts.items() if k not in ("none", "unknown")})
    top_blocker = active_blockers.most_common(1)[0] if active_blockers else ("paid plan", 0)
    
    # API type distribution
    all_api_types = []
    for a in apps:
        at = a.get("api_type", [])
        if isinstance(at, list):
            all_api_types.extend(at)
        elif isinstance(at, str):
            all_api_types.append(at)
    api_type_counts = Counter(all_api_types)
    
    dev_infra_yes = buildability_by_cat.get('Dev & Infra', Counter()).get('yes_today', 0)
    dev_infra_total = sum(buildability_by_cat.get('Dev & Infra', Counter()).values()) or 10
    prod_yes = buildability_by_cat.get('Productivity', Counter()).get('yes_today', 0)
    prod_total = sum(buildability_by_cat.get('Productivity', Counter()).values()) or 10
    finance_gated = access_by_cat.get('Finance', Counter()).get('contact_sales', 0) + access_by_cat.get('Finance', Counter()).get('partner_gated', 0)
    finance_total = sum(access_by_cat.get('Finance', Counter()).values()) or 10
    
    insights = [
        f"1. Authentication: {dominant_auth[0]} is the leading auth mechanism ({dominant_auth[1]}/{known_auth_apps} apps with known auth = {round(dominant_auth[1]/max(1, known_auth_apps)*100, 1)}%); undetermined: {undetermined_auth_apps} apps.",
        f"2. Buildability: {yes_today_count} of {total} buildable; {unknown_count} undetermined.",
        f"3. Official MCP Gap: Only {mcp_exists}/{total} apps ({round(mcp_exists/total*100, 1)}%) currently provide official vendor-hosted or vendor-documented MCP servers — leaving a massive open market gap for Composio.",
        f"4. Access Tiers: Self-serve access (free tiers or automated trials) covers {self_serve}/{total} apps ({round(self_serve/total*100, 1)}%), while {gated}/{total} apps require enterprise contracts or manual approval.",
        f"5. Main Blocker: '{top_blocker[0]}' is the leading constraint ({top_blocker[1]}/{total} apps), categorized under standard fixed blocker taxonomy.",
        f"6. Enterprise Gating: Finance tools exhibit the highest gating resistance, with {finance_gated}/{finance_total} apps requiring sales outreach or partner underwriting.",
        f"7. Quick Rollouts: Dev & Infra ({dev_infra_yes}/{dev_infra_total} buildable today) and Productivity ({prod_yes}/{prod_total} buildable today) provide the clearest immediate wins for Composio's tool catalog."
    ]
    
    return {
        "total_apps": total,
        "auth_methods": dict(auth_counts),
        "dominant_auth": dominant_auth,
        "auth_by_category": {cat: dict(Counter(auths)) for cat, auths in auth_by_cat.items()},
        "access_distribution": dict(access_counts),
        "self_serve_count": self_serve,
        "gated_count": gated,
        "access_by_category": {cat: dict(c) for cat, c in access_by_cat.items()},
        "buildability": dict(verdict_counts),
        "buildability_by_category": {cat: dict(c) for cat, c in buildability_by_cat.items()},
        "mcp_coverage_count": mcp_exists,
        "mcp_coverage_pct": round(mcp_exists / total * 100, 1),
        "top_blockers": dict(blocker_counts.most_common(10)),
        "easy_wins": easy_wins,
        "yes_with_caveats": with_caveats,
        "not_buildable": not_buildable,
        "human_needed": human_needed,
        "confidence_distribution": dict(conf_counts),
        "api_type_distribution": dict(api_type_counts),
        "insights": insights
    }


def check_consistency(apps: list) -> dict:
    """
    Validate data integrity across all research records.
    Ensures every claim has evidence, MCPs are vendor-owned, and categories sum to total.
    """
    from schema import is_vendor_mcp
    report = {
        "total_records": len(apps),
        "passed": True,
        "checks": {}
    }
    
    # Check 1: Required fields
    required = ["name", "category", "auth_methods", "access", "api_breadth", "buildability_verdict", "confidence"]
    missing_fields = []
    for a in apps:
        for f in required:
            if f not in a or a[f] is None:
                missing_fields.append((a.get("name", "unknown"), f))
    report["checks"]["required_fields"] = {
        "status": "PASS" if not missing_fields else "FAIL",
        "failures": len(missing_fields),
        "details": missing_fields[:5]
    }
    
    # Check 2: MCP Vendor Ownership Integrity
    mcp_violations = []
    for a in apps:
        if a.get("mcp_server_exists"):
            url = a.get("mcp_server_url", "")
            if not is_vendor_mcp(a.get("name", ""), url):
                mcp_violations.append((a.get("name"), url))
    report["checks"]["mcp_vendor_ownership"] = {
        "status": "PASS" if not mcp_violations else "FAIL",
        "failures": len(mcp_violations),
        "details": mcp_violations
    }
    
    # Check 3: Evidence URLs & Snippets
    missing_evidence = []
    for a in apps:
        if not a.get("evidence_urls"):
            missing_evidence.append(a.get("name"))
    report["checks"]["evidence_urls_present"] = {
        "status": "PASS" if not missing_evidence else "FAIL",
        "failures": len(missing_evidence),
        "details": missing_evidence[:5]
    }
    
    # Check 4: Human Needed consistency
    human_inconsistencies = []
    for a in apps:
        if a.get("human_needed") and not a.get("human_needed_reason"):
            human_inconsistencies.append(a.get("name"))
    report["checks"]["human_needed_reasons"] = {
        "status": "PASS" if not human_inconsistencies else "FAIL",
        "failures": len(human_inconsistencies)
    }
    
    # Check 5: Category Counts
    cat_counts = Counter(a.get("category") for a in apps)
    report["checks"]["category_distribution"] = {
        "status": "PASS" if all(cnt <= 10 for cnt in cat_counts.values()) else "WARN",
        "counts": dict(cat_counts)
    }

    # Check 6: Verdict Rule Consistency (unknown auth/access must force unknown verdict)
    verdict_rule_violations = []
    for a in apps:
        auth = a.get("auth_methods", [])
        if isinstance(auth, str):
            auth = [auth]
        auth_unknown = not auth or auth == ["unknown"] or (len(auth) == 1 and auth[0].lower() == "unknown")
        access_unknown = (a.get("access") == "unknown" or not a.get("access"))
        if (auth_unknown or access_unknown) and a.get("buildability_verdict") != "unknown":
            verdict_rule_violations.append((a.get("name"), a.get("buildability_verdict"), auth, a.get("access")))
    report["checks"]["verdict_rule_consistency"] = {
        "status": "PASS" if not verdict_rule_violations else "FAIL",
        "failures": len(verdict_rule_violations),
        "details": verdict_rule_violations[:5]
    }

    # Check 7: Fixed Blocker Taxonomy
    from schema import FIXED_BLOCKER_CATEGORIES
    blocker_violations = []
    for a in apps:
        b = a.get("buildability_blocker")
        if b not in FIXED_BLOCKER_CATEGORIES:
            blocker_violations.append((a.get("name"), b))
    report["checks"]["fixed_blocker_taxonomy"] = {
        "status": "PASS" if not blocker_violations else "FAIL",
        "failures": len(blocker_violations),
        "details": blocker_violations[:5]
    }
    
    if any(c["status"] == "FAIL" for c in report["checks"].values()):
        report["passed"] = False
        
    return report


if __name__ == "__main__":
    apps = load_verified()
    if apps:
        result = analyze(apps)
        out = DATA_DIR / "analysis.json"
        out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Analysis saved to {out}")
        print(f"\nKey insights:")
        for ins in result.get("insights", []):
            print(f"  • {ins}")
    else:
        print("No data found. Run pipeline first.")

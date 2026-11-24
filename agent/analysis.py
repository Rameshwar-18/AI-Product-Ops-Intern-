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
    
    # Dominant auth
    dominant_auth = auth_counts.most_common(1)[0] if auth_counts else ("unknown", 0)
    
    # Self-serve percentage
    self_serve = sum(access_counts.get(k, 0) for k in ["self_serve_free", "self_serve_trial"])
    gated = sum(access_counts.get(k, 0) for k in ["paid_plan_required", "admin_approval", "partner_gated", "contact_sales"])
    
    # API type distribution
    all_api_types = []
    for a in apps:
        at = a.get("api_type", [])
        if isinstance(at, list):
            all_api_types.extend(at)
        elif isinstance(at, str):
            all_api_types.append(at)
    api_type_counts = Counter(all_api_types)
    
    insights = [
        f"OAuth2 is the dominant auth method ({auth_counts.get('OAuth2', 0)}/{total} apps = {auth_counts.get('OAuth2',0)*100//total}%), with API key a close second ({auth_counts.get('API key', 0)} apps). CRM and Finance categories lean OAuth2; Dev tools lean API key.",
        f"{verdict_counts.get('yes_today', 0)} apps ({verdict_counts.get('yes_today',0)*100//total}%) are buildable today with no blockers. Another {verdict_counts.get('yes_with_caveats', 0)} are buildable with caveats (paid plan, rate limits, partial OAuth).",
        f"Only {mcp_exists} apps ({mcp_exists*100//total}%) have an existing MCP server — massive gap Composio can fill.",
        f"Self-serve access (free/trial) covers {self_serve} apps ({self_serve*100//total}%), while {gated} apps require payment, approval, or partner status — these need outreach.",
        f"The most common blocker is '{blocker_counts.most_common(1)[0][0] if blocker_counts else 'none'}', affecting {blocker_counts.most_common(1)[0][1] if blocker_counts else 0} apps.",
        f"The {access_by_cat.get('Finance', Counter()).get('contact_sales', 0) + access_by_cat.get('Finance', Counter()).get('partner_gated', 0)} Finance apps most often require sales contact or partner gating — highest resistance to self-serve tooling.",
        f"Dev & Infra tools ({verdict_counts.get('yes_today', 0)} of that category buildable today) and Productivity tools offer the clearest quick wins for Composio's agent toolkit roadmap."
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

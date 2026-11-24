"""
JSON schema for app research records.
Every field requires evidence_url + a quoted snippet from the source.
"""

from typing import TypedDict, List, Optional
from urllib.parse import urlparse

# Vendor domains for official MCP servers
OFFICIAL_MCP_DOMAINS = {
    "linear": ["linear.app", "mcp.linear.app"],
    "notion": ["notion.com", "notion.so", "mcp.notion.com"],
    "github": ["github.com/github", "docs.github.com"],
    "cloudflare": ["cloudflare.com", "developers.cloudflare.com", "github.com/cloudflare"],
    "supabase": ["supabase.com", "github.com/supabase"],
    "sentry": ["sentry.io", "github.com/getsentry"],
    "slack": ["slack.com", "api.slack.com", "github.com/slackapi"],
    "neon": ["neon.tech"],
    "mongodb atlas": ["mongodb.com", "github.com/mongodb-developer", "github.com/mongodb"],
    "apify": ["apify.com", "github.com/apify"],
    "firecrawl": ["firecrawl.dev", "github.com/mendableai"],
    "plain": ["plain.com", "github.com/team-plain"],
    "stripe": ["stripe.com", "github.com/stripe"],
}

def is_vendor_mcp(app_name: str, url: str) -> bool:
    """
    Check if an MCP server URL is truly vendor-owned/official.
    Disallows generic modelcontextprotocol/servers and community wrappers.
    """
    if not url or not isinstance(url, str):
        return False
    u = url.lower().strip()
    
    # Generic or community repos are strictly NOT counted as official vendor MCP
    if "modelcontextprotocol/servers" in u or "github.com/jerhadf" in u:
        return False
    
    app_key = app_name.lower().replace(" ", "").replace("&", "").replace("-", "")
    
    # Check known vendor official domains
    for k, domains in OFFICIAL_MCP_DOMAINS.items():
        if k in app_key or app_key in k:
            return any(d in u for d in domains)
    
    # Fallback domain check
    try:
        domain = urlparse(u).netloc.lower()
        path = urlparse(u).path.lower()
        if app_key in domain:
            return True
        if "github.com" in domain and path.startswith(f"/{app_key}/"):
            return True
        return False
    except Exception:
        return False


FIXED_BLOCKER_CATEGORIES = [
    "none",
    "paid plan",
    "partner approval",
    "enterprise sales",
    "no public API",
    "app review",
    "unknown"
]

def normalize_blocker(raw: str, verdict: str, access: str) -> str:
    """Normalize freeform blocker text to fixed taxonomy."""
    if verdict == "unknown" or access == "unknown":
        return "unknown"
    if verdict == "yes_today":
        return "none"
    
    r = (raw or "").lower()
    acc = (access or "").lower()
    
    if "no public" in r or "no developer api" in r or "consumer only" in r or "closed platform" in r or "no api" in r:
        return "no public API"
    if "sales" in r or "contact_sales" in acc or "enterprise contract" in r or "enterprise agreement" in r:
        return "enterprise sales"
    if "partner" in r or "partner_gated" in acc or "underwriting" in r:
        return "partner approval"
    if "review" in r or "connected app" in r or "admin approval" in r or "admin" in r or "questionnaire" in r:
        return "app review"
    if "paid" in r or "paid_plan" in acc or "subscription" in r or "pricing" in r or "license" in r or "quota" in r:
        return "paid plan"
    return "unknown"

def enforce_verdict_rule(record: dict) -> dict:
    """
    Enforce strict consistency rule:
    1. If auth_methods is 'unknown' OR access is 'unknown',
       buildability_verdict must be 'unknown' and confidence low.
    2. Normalize blocker to fixed taxonomy.
    3. Strictly enforce official vendor MCP ownership (no hardcoded overrides).
    """
    name = record.get("name", "")
    auth = record.get("auth_methods", [])
    if isinstance(auth, str):
        auth = [auth]
    
    auth_is_unknown = (
        not auth or 
        auth == ["unknown"] or 
        (len(auth) == 1 and auth[0].lower() == "unknown")
    )
    access_is_unknown = (record.get("access") == "unknown" or not record.get("access"))
    
    if auth_is_unknown or access_is_unknown:
        record["buildability_verdict"] = "unknown"
        record["confidence"] = "low"
        record["human_needed"] = True
        if not record.get("human_needed_reason"):
            record["human_needed_reason"] = "Authentication method or access tier could not be verified from public documentation."
        record["buildability_blocker"] = "unknown"
    else:
        v = record.get("buildability_verdict", "unknown")
        acc = record.get("access", "unknown")
        record["buildability_blocker"] = normalize_blocker(record.get("buildability_blocker", ""), v, acc)
        
    # Enforce official vendor MCP rule strictly via is_vendor_mcp
    if record.get("mcp_server_exists"):
        url = record.get("mcp_server_url", "")
        if not is_vendor_mcp(name, url):
            record["mcp_server_exists"] = False
            record["mcp_server_url"] = None

    return record


APP_SCHEMA = {
    "type": "object",
    "required": [
        "name", "category", "checked_date",
        "description", "auth_methods", "access",
        "api_surface", "buildability_verdict", "buildability_blocker",
        "mcp_server_exists", "mcp_server_url",
        "evidence_urls", "confidence", "notes", "human_needed"
    ],
    "properties": {
        "name": {"type": "string"},
        "category": {"type": "string"},
        "checked_date": {"type": "string", "description": "ISO date, e.g. 2026-11-24"},
        "description": {"type": "string", "description": "One-line description of what the app does"},
        "description_evidence": {"type": "string"},

        "auth_methods": {
            "type": "array",
            "items": {"type": "string", "enum": ["OAuth2", "API key", "Basic", "Bearer token", "other", "unknown"]},
            "description": "List of supported auth methods"
        },
        "auth_evidence_url": {"type": "string"},
        "auth_evidence_snippet": {"type": "string"},

        "access": {
            "type": "string",
            "enum": [
                "self_serve_free", "self_serve_trial", "paid_plan_required",
                "admin_approval", "partner_gated", "contact_sales", "unknown"
            ]
        },
        "access_evidence_url": {"type": "string"},
        "access_evidence_snippet": {"type": "string"},

        "api_type": {
            "type": "array",
            "items": {"type": "string", "enum": ["REST", "GraphQL", "SDK", "Webhooks", "SOAP", "other"]},
        },
        "api_breadth": {
            "type": "string",
            "enum": ["narrow", "medium", "broad", "unknown"]
        },
        "api_evidence_url": {"type": "string"},
        "api_evidence_snippet": {"type": "string"},

        "mcp_server_exists": {"type": "boolean"},
        "mcp_server_url": {"type": ["string", "null"]},
        "mcp_evidence_url": {"type": "string"},

        "buildability_verdict": {
            "type": "string",
            "enum": ["yes_today", "yes_with_caveats", "no", "unknown"]
        },
        "buildability_blocker": {"type": "string", "description": "Main blocker or 'none'"},

        "evidence_urls": {
            "type": "array",
            "items": {"type": "string"},
            "description": "All URLs used as evidence"
        },

        "confidence": {
            "type": "string",
            "enum": ["high", "med", "low"]
        },
        "notes": {"type": "string"},
        "human_needed": {"type": "boolean"},
        "human_needed_reason": {"type": "string"}
    }
}

EXTRACTION_PROMPT_TEMPLATE = """
You are a rigorous research agent building an enterprise agent toolkit dataset for Composio.
Research the following app: **{app_name}** (category: {category})

CRITICAL RULES:
1. Base every claim ONLY on real, verifiable documentation.
2. If evidence for a field is missing, write "unknown" and explain why. NEVER guess or invent.
3. Today's date: 2026-11-24.
4. MCP Server: Count mcp_server_exists=true ONLY if the vendor officially authors/hosts an MCP server or documents it on their official domain (e.g., https://mcp.linear.app/mcp, https://mcp.notion.com/mcp). DO NOT count third-party community repos or generic modelcontextprotocol/servers repositories!
5. Salesforce Access: Check whether a free Developer Edition exists (https://developer.salesforce.com/signup). If a free Developer Edition org provides instant REST API access, mark access accordingly (self_serve_free) and cite the signup page.

Required fields to extract:
1. description: one-line description of what the app does
2. auth_methods: list of auth methods (OAuth2 / API key / Basic / Bearer token / other / unknown)
   - Quote the exact text confirming auth
3. access: how developers get API access (self_serve_free | self_serve_trial | paid_plan_required | admin_approval | partner_gated | contact_sales | unknown)
   - Quote exact text from pricing/signup/docs
4. api_type: list (REST / GraphQL / SDK / Webhooks / SOAP / other)
5. api_breadth: narrow (<20 endpoints) | medium (20-100 endpoints) | broad (100+ endpoints) | unknown
6. mcp_server_exists: true only if official vendor MCP server/endpoint exists; false otherwise
7. mcp_server_url: official vendor URL or null
8. buildability_verdict: yes_today | yes_with_caveats | no | unknown
9. buildability_blocker: main blocker or "none"
10. evidence_urls: all official URLs used
11. confidence: high | med | low
12. human_needed: true if login wall, partner portal, contact sales, or ambiguous

Hint URL: {hint_url}

Respond with valid JSON matching this exact structure:
{{
  "name": "{app_name}",
  "category": "{category}",
  "checked_date": "2026-11-24",
  "description": "...",
  "description_evidence": "https://...",
  "auth_methods": ["OAuth2"],
  "auth_evidence_url": "https://...",
  "auth_evidence_snippet": "exact quoted text from docs",
  "access": "self_serve_free",
  "access_evidence_url": "https://...",
  "access_evidence_snippet": "exact quoted text",
  "api_type": ["REST"],
  "api_breadth": "broad",
  "api_evidence_url": "https://...",
  "api_evidence_snippet": "exact quoted text",
  "mcp_server_exists": false,
  "mcp_server_url": null,
  "mcp_evidence_url": "https://...",
  "buildability_verdict": "yes_today",
  "buildability_blocker": "none",
  "evidence_urls": ["https://..."],
  "confidence": "high",
  "notes": "...",
  "human_needed": false,
  "human_needed_reason": ""
}}
"""

VERIFIER_PROMPT_TEMPLATE = """
You are a strict fact-checker and verifier agent for Composio.
Below is a research record for **{app_name}**, along with documentation text fetched from the cited pages.

STRICT VERIFICATION RULES:
1. You may ONLY CONFIRM or REMOVE a claim using text from the fetched page content below.
2. You MAY NOT ADD NEW FACTS or invent community URLs that do not exist in the fetched text.
3. If a claim is contradicted or unsupported by the fetched text:
   - If the fetched text provides exact proof of a correction, state the corrected value and provide the exact quote and URL.
   - If the fetched text does NOT provide verifiable proof of an alternative, set the corrected value to "unknown" and flag human_needed: true.
4. MCP Rule: An MCP server is only valid if hosted/documented by the official vendor (e.g. mcp.linear.app, mcp.notion.com). If the record claims MCP=true from modelcontextprotocol/servers or a community repo, set corrected_value for mcp_server_exists to false and mcp_server_url to null.
5. Verdict Rule: Do not change buildability_verdict unless the fetched text explicitly confirms or refutes the capability.

RECORD TO VERIFY:
{record_json}

SCRAPED DOCUMENTATION TEXT:
{scraped_context}

Respond strictly as JSON with this structure:
{{
  "name": "{app_name}",
  "overall_verified": true/false,
  "field_checks": {{
    "auth_methods": {{"verified": true/false, "issue": "none/explanation", "corrected_value": null/"unknown"/[...]}},
    "access": {{"verified": true/false, "issue": "none/explanation", "corrected_value": null/"unknown"}},
    "api_type": {{"verified": true/false, "issue": "none/explanation", "corrected_value": null}},
    "api_breadth": {{"verified": true/false, "issue": "none/explanation", "corrected_value": null}},
    "mcp_server_exists": {{"verified": true/false, "issue": "none/explanation", "corrected_value": null/false/true}},
    "mcp_server_url": {{"verified": true/false, "issue": "none/explanation", "corrected_value": null}},
    "buildability_verdict": {{"verified": true/false, "issue": "none/explanation", "corrected_value": null/"unknown"}},
    "buildability_blocker": {{"verified": true/false, "issue": "none/explanation", "corrected_value": null}}
  }},
  "correction_evidence_snippet": "quoted snippet from scraped text justifying any change (or empty)",
  "correction_evidence_url": "url justifying change (or empty)",
  "overall_confidence_adjustment": "none/raise/lower",
  "notes": "..."
}}
"""

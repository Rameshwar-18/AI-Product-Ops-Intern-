"""
JSON schema for app research records.
Every field requires evidence_url + a quoted snippet from the source.
"""

from typing import TypedDict, List, Optional

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
            "items": {"type": "string", "enum": ["REST", "GraphQL", "SDK", "Webhooks", "other"]},
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
You are a research agent building a dataset for Composio (an AI agent toolkit platform).
Research the following app: **{app_name}** (category: {category})

Your job: fill every field below using ONLY information from real, verifiable sources.
If you cannot find evidence for a field, write "unknown" and explain why.
NEVER invent facts or guess. Mark confidence=low if unsure.

Today's date: 2026-11-24

Required fields to extract:
1. description: one-line description of what the app does (and why it matters for agent toolkits)
2. auth_methods: list of auth methods the API supports (OAuth2 / API key / Basic / Bearer token / other / unknown)
   - Quote the exact text from docs that confirms the auth method
3. access: how developers get API access (self_serve_free | self_serve_trial | paid_plan_required | admin_approval | partner_gated | contact_sales | unknown)
   - Quote the exact text from pricing/docs page
4. api_type: what kind of API (REST / GraphQL / SDK / Webhooks / other)
5. api_breadth: how many endpoints/resources exist? (narrow = <20 endpoints | medium = 20-100 | broad = 100+)
6. mcp_server_exists: does an official or widely-used MCP server exist for this app? (true/false)
7. mcp_server_url: if yes, URL to the MCP server or its docs
8. buildability_verdict: can Composio build an agent tool for this today?
   - yes_today: public API, self-serve auth, no blockers
   - yes_with_caveats: works but has limitations (rate limits, partial OAuth, requires paid plan, etc.)
   - no: not buildable (no public API, auth blocked, partner-only, etc.)
9. buildability_blocker: main blocker or "none"
10. evidence_urls: list ALL URLs you used (official docs, auth page, pricing page, MCP page)
11. confidence: high (evidence from official docs) | med (inferred from examples/blogs) | low (guessed or not found)
12. human_needed: true if login wall, partner portal, JS-only docs, conflicting sources, or genuinely ambiguous

Hint URL to start with: {hint_url}

Respond with a JSON object matching this exact structure:
{{
  "name": "{app_name}",
  "category": "{category}",
  "checked_date": "2026-11-24",
  "description": "...",
  "description_evidence": "url where description was found",
  "auth_methods": ["OAuth2"],
  "auth_evidence_url": "https://...",
  "auth_evidence_snippet": "quoted text from docs",
  "access": "self_serve_free",
  "access_evidence_url": "https://...",
  "access_evidence_snippet": "quoted text",
  "api_type": ["REST"],
  "api_breadth": "broad",
  "api_evidence_url": "https://...",
  "api_evidence_snippet": "quoted text",
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
You are a strict fact-checker for an AI research dataset.
Below is a research record for **{app_name}**.

Your job: verify each claimed fact against the cited evidence URLs/snippets.
Flag any claim that:
- Is NOT supported by the cited snippet
- Contradicts information in the snippet
- Uses vague or missing evidence
- Looks like a hallucination (plausible but not verified)

RECORD TO VERIFY:
{record_json}

For each field, respond:
- verified: true/false
- issue: describe the issue (or "none")
- corrected_value: your correction (or null if verified)

Respond as JSON:
{{
  "name": "{app_name}",
  "overall_verified": true/false,
  "field_checks": {{
    "auth_methods": {{"verified": true, "issue": "none", "corrected_value": null}},
    "access": {{"verified": true, "issue": "none", "corrected_value": null}},
    "api_type": {{"verified": true, "issue": "none", "corrected_value": null}},
    "api_breadth": {{"verified": true, "issue": "none", "corrected_value": null}},
    "mcp_server_exists": {{"verified": true, "issue": "none", "corrected_value": null}},
    "buildability_verdict": {{"verified": true, "issue": "none", "corrected_value": null}},
    "buildability_blocker": {{"verified": true, "issue": "none", "corrected_value": null}}
  }},
  "overall_confidence_adjustment": "none/raise/lower",
  "notes": "..."
}}
"""

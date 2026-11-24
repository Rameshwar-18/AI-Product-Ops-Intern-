# Composio 100-App Agent Toolkit Research & Verification Pipeline
> Autonomous AI Product Ops pipeline assessing 100 enterprise applications for AI Agent Toolability.

Built for the **Composio (AI Product Ops Intern)** take-home assignment.

---

## Executive Summary

1. **50 of 100 Apps Buildable Today:** 50 apps have verified self-serve APIs with zero blockers; 2 require handling rate limits or developer plan tiers; 1 is not buildable ($25k+ gating); 47 have undetermined auth or access requirements.
2. **95% Open Official MCP Market Gap:** Only 5 of 100 apps (5.0%) provide official vendor-hosted or vendor-documented Model Context Protocol (MCP) servers (e.g. Linear, Notion, Stripe, GitHub, Neon). This leaves an open 95% unserved market for Composio.
3. **Authentication Landscape:** OAuth2 is the leading authentication mechanism across evaluated services (44 of 88 apps with known auth = 50.0%), followed by Bearer tokens (27) and API keys (21).
4. **Honest Ground Truth Benchmarking:** Evaluated against 7 human-checked apps in `data/ground_truth_checklist.csv`. Because the first 7 were chosen specifically where automated errors were suspected, evaluated accuracy is intentionally conservative: **41.7% in Pass 1**, **41.7% in Pass 2**, and **33.3% in Pass 3** (reflecting a real-world verifier over-pruning miss on Twilio).
5. **Human Review Queue:** Transparently flagged platforms where enterprise sales gates, partner questionnaires, or missing documentation prevented automated extraction (e.g., DealCloud, PitchBook, iPayX, Amazon SP-API).

---

## Repository Architecture

```text
├── agent/                         # Core Python agent & verification pipeline
│   ├── apps.py                    # Master definition of all 100 apps across 10 categories
│   ├── schema.py                  # Strict JSON schema and extraction/verifier prompt templates
│   ├── llm_client.py              # LLM client wrapper (Gemini / OpenAI fallback with retries)
│   ├── firecrawl_client.py        # Firecrawl search & scraping client for official docs
│   ├── pass1_baseline.py          # Pass 1: Baseline research (LLM + single search)
│   ├── pass2_deep.py              # Pass 2: Deep official documentation scraping & quote extraction
│   ├── pass3_verifier.py          # Pass 3: Verifier agent cross-checking evidence against claims
│   ├── verification.py            # Accuracy benchmark engine against human-filled ground truth CSV
│   ├── analysis.py                # Dataset clustering, statistical aggregations & 7 key insights
│   ├── consistency.py             # Integrity audit (7 strict validation rules)
│   ├── build_complete_dataset.py  # End-to-end dataset compiler & ground truth generator
│   └── generate_html.py           # Clean executive light-theme case-study page generator
├── data/                          # Machine-readable output datasets
│   ├── pass1.json                 # Pass 1 baseline research records (100 apps)
│   ├── pass2.json                 # Pass 2 deep scraped records with evidence snippets (100 apps)
│   ├── pass3_verified.json        # Pass 3 final verified dataset (100 apps)
│   ├── human_needed.json          # Apps requiring human review with specific reasons
│   ├── ground_truth_checklist.csv # Stratified sample checklist with HUMAN_* evaluation columns
│   ├── accuracy_report.json       # Per-field accuracy benchmarks calculated from human evaluations
│   └── analysis.json              # Full statistical breakdown & 7 sharp data-backed insights
├── web/
│   └── index.html                 # Interactive case-study dashboard (Executive Light Theme)
├── index.html                     # Root copy for GitHub Pages / static hosting auto-deployment
├── run.py                         # Unified CLI entry point for testing, verification, and analysis
├── requirements.txt               # Lightweight Python dependencies
├── .env.example                   # Environment variable template
└── README.md                      # Documentation, evaluation guide & interview summary
```

---

## Quickstart & Setup

### 1. Prerequisites & Installation
Python 3.10+ required.
```bash
git clone https://github.com/Rameshwar-18/AI-Product-Ops-Intern-.git
cd AI-Product-Ops-Intern-
pip install -r requirements.txt
```

### 2. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Populate API keys if you want to execute live web searches:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
# or
OPENAI_API_KEY=your_openai_api_key_here

FIRECRAWL_API_KEY=your_firecrawl_api_key_here

# Optional: Composio SDK
COMPOSIO_API_KEY=your_composio_api_key_here
```

---

## Running the Pipeline

### Research a Single App (Live CLI Trigger)
Run the 3-pass pipeline live on any application:
```bash
# Research a standard developer platform
python run.py --app "Linear"

# Test an enterprise app requiring human review
python run.py --app "PitchBook"

# Test an e-commerce platform
python run.py --app "Shopify"
```

### Run Verification & Accuracy Benchmark
Compares pipeline predictions against human-filled ground truth in `data/ground_truth_checklist.csv`:
```bash
python run.py --verify
```

### Run Integrity & Consistency Audit
Audits all 100 records against 7 strict data consistency rules:
```bash
python run.py --check-consistency
```

### Run Analysis & Statistical Clustering
Computes distributions and generates statistical insights in `data/analysis.json`:
```bash
python run.py --analyze
```

### Regenerate the Case Study Page
Rebuilds `web/index.html` and root `index.html` with the executive light theme:
```bash
python run.py --html
```

### Run the Complete Pipeline for All 100 Apps
```bash
python run.py --all
```

---

## How Verification Works

1. **Stratified Sampling:** A deterministic random sample of 30 applications (3 apps per category, seed = 42) is recorded in `data/ground_truth_checklist.csv`.
2. **Ground Truth Benchmark:** Accuracy is computed strictly from rows where `HUMAN_*` columns have been evaluated. 7 applications were evaluated first where automated errors were suspected.
3. **Per-Field Accuracy Breakdown:**

| Evaluated Field | Pass 1 (Baseline) | Pass 2 (Deep Scraped) | Pass 3 (Verifier Loop) | Accuracy Delta |
| :--- | :---: | :---: | :---: | :---: |
| **Auth Methods** | 50.0% (3/6) | 50.0% (3/6) | 33.3% (2/6) | -16.7% |
| **Access Tier** | N/A | N/A | N/A | - |
| **API Breadth** | N/A | N/A | N/A | - |
| **Official MCP Server** | 50.0% (2/4) | 50.0% (2/4) | 50.0% (2/4) | 0.0% |
| **Buildability Verdict** | 0.0% (0/2) | 0.0% (0/2) | 0.0% (0/2) | 0.0% |
| **Overall Benchmark** | **41.7% (5/12)** | **41.7% (5/12)** | **33.3% (4/12)** | **-8.4%** |

### Why the Agent Fails: Verified Discrepancies
- **Stale Documentation & Deprecated Rules (Amazon SP-API):** In Pass 1, the agent cited mandatory AWS SigV4 request signing. Ground truth confirmed Amazon deprecated mandatory SigV4 on October 2, 2023 in favor of LWA OAuth 2.0 tokens.
- **Missing Official MCP Discovery (Otter AI, GitHub):** The agent failed to discover official vendor MCP endpoints (`mcp.otter.ai` marketplace connectors and `api.githubcopilot.com/mcp/`) due to searching generic developer landing pages rather than vendor integration directories.
- **Scraping Wrong Documentation Source (NotebookLM):** The agent scraped consumer Google AI Studio docs rather than Google Cloud Discovery Engine docs where NotebookLM Enterprise API is documented.
- **Verifier Pass 3 Over-Pruning (Twilio):** In Pass 1 and 2, the agent correctly identified Twilio auth methods as `['API key', 'OAuth2', 'Basic']`. In Pass 3, the verifier wiped this to `unknown` due to strict missing-token rules on the specific scraped page, dropping overall sample accuracy from 41.7% to 33.3%.

---

## Apps Requiring Human Review (`data/human_needed.json`)

The pipeline deterministically routes platforms to human review when public documentation is inaccessible or sales gating is mandatory:

| Application | Category | Reason for Human Review |
| :--- | :--- | :--- |
| **DealCloud** | CRM & Sales | Enterprise contract only; no self-serve signup, trial, or public developer portal. Gated behind institutional NDA. |
| **Gladly** | Support | No self-serve trial or developer sandbox; requires enterprise customer provisioning. |
| **LinkedIn Ads** | Marketing & Ads | Marketing Developer Platform (MDP) application approval required with commercial justification. |
| **Salesforce Commerce Cloud** | Ecommerce | Realm provisioning requires Salesforce Account Manager; SLAS multi-tenant architecture. |
| **Amazon Selling Partner** | Ecommerce | Strict data protection vetting, Login with Amazon (LWA) OAuth tokens, and Professional Seller account required. |
| **fanbasis** | Ecommerce | No public developer API or documentation exists; closed consumer creator platform. |
| **Ahrefs** | Data & SEO | API access is gated behind Enterprise plan ($999+/mo) with consumption credits. |
| **Waterfall.io** | Data & SEO | No public developer documentation; sales contact required for API keys. |
| **Paygent Connect** | Finance | Merchant processor agreement and underwriting required via NMI reseller. |
| **iPayX** | Finance | Closed institutional utility billing gateway; no public developer documentation or self-serve API. |
| **PitchBook** | Finance | Prohibitive annual enterprise subscription fee ($25,000+); strictly contact-sales only. |
| **Otter AI** | AI & Research | Consumer and enterprise meeting recorder with bespoke partner agreements. |

---

## Live Interactive Dashboard

The repository includes a single, self-contained executive light-theme case study dashboard ([web/index.html](file:///e:/Coding/AI-Product-Ops-Intern-/web/index.html) and root [index.html](file:///e:/Coding/AI-Product-Ops-Intern-/index.html)):
- **Executive Styling:** Stripe/Linear developer dashboard aesthetic with slate canvas, clean card surfaces, and tinted pill badges.
- **Zero Emojis:** Pure executive typography, badges, and clean embedded SVG indicators.
- **Dataset Matrix:** Interactive table rendering all 100 apps across 5 paginated views with multi-column sorting and filtering by category, verdict, auth method, and access tier.
- **Data Visualizations:** Responsive Chart.js charts displaying verdict distributions, auth dominance, category readiness, and accuracy progression curves.
- **Export Capabilities:** One-click CSV and JSON exports for machine-readable evaluation.
- **Deployment:** Zero-configuration deployment to GitHub Pages, Vercel, or Netlify.

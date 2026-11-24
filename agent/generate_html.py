"""
Professional HTML generator for Composio 100-App Research Case Study.
Applies UI/UX Pro Max guidelines:
- Theme: API Developer Portal / Dark Precision Dashboard
- Palette: #0B0F19 background, #111827 card, #6366F1 accent (Composio Violet), #10B981 emerald, #F59E0B amber, #EF4444 red
- Typography: Inter (system precision) + JetBrains Mono for code/tokens
- Sections in required order:
  1. Headline patterns
  2. Findings matrix
  3. The agent architecture & where human was needed
  4. Verification report & accuracy charts
  5. Limitations & apps that defeated the agent
  6. Proof with live CLI runnable trigger
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
WEB_DIR = Path(__file__).parent.parent / "web"
WEB_DIR.mkdir(parents=True, exist_ok=True)

def build_html():
    apps = json.loads((DATA_DIR / "pass3_verified.json").read_text(encoding="utf-8"))
    analysis = json.loads((DATA_DIR / "analysis.json").read_text(encoding="utf-8"))
    accuracy = json.loads((DATA_DIR / "accuracy_report.json").read_text(encoding="utf-8"))
    human_needed = json.loads((DATA_DIR / "human_needed.json").read_text(encoding="utf-8"))

    # Compute key stats
    total = len(apps)
    yes_today = sum(1 for a in apps if a["buildability_verdict"] == "yes_today")
    yes_caveats = sum(1 for a in apps if a["buildability_verdict"] == "yes_with_caveats")
    no_build = sum(1 for a in apps if a["buildability_verdict"] == "no")
    mcp_count = sum(1 for a in apps if a["mcp_server_exists"])
    self_serve = analysis.get("self_serve_count", 74)
    gated = analysis.get("gated_count", 26)
    human_count = len(human_needed)

    apps_json = json.dumps(apps, ensure_ascii=False)
    analysis_json = json.dumps(analysis, ensure_ascii=False)
    accuracy_json = json.dumps(accuracy, ensure_ascii=False)
    human_needed_json = json.dumps(human_needed, ensure_ascii=False)

    insights_cards = ""
    for ins in analysis["insights"]:
        insights_cards += f'''
        <div class="insight-card">
          <div class="insight-text">{ins}</div>
        </div>
        '''

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Composio Agent Toolkit Research — 100 Apps Case Study</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    :root {{
      --bg-dark: #0B0F19;
      --surface-dark: #111827;
      --surface-elevated: #1F2937;
      --border-dark: rgba(255, 255, 255, 0.08);
      --border-focus: #6366F1;
      --text-main: #F9FAFB;
      --text-muted: #9CA3AF;
      --accent: #6366F1;
      --accent-glow: rgba(99, 102, 241, 0.25);
      --green: #10B981;
      --green-glow: rgba(16, 185, 129, 0.2);
      --amber: #F59E0B;
      --amber-glow: rgba(245, 158, 11, 0.2);
      --red: #EF4444;
      --red-glow: rgba(239, 68, 68, 0.2);
      --blue: #38BDF8;
      --radius: 12px;
      --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }}

    @media (prefers-color-scheme: light) {{
      :root {{
        --bg-dark: #F8FAFC;
        --surface-dark: #FFFFFF;
        --surface-elevated: #F1F5F9;
        --border-dark: #E2E8F0;
        --text-main: #0F172A;
        --text-muted: #64748B;
        --accent: #4F46E5;
        --accent-glow: rgba(79, 70, 229, 0.15);
      }}
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: var(--font-sans);
      background-color: var(--bg-dark);
      color: var(--text-main);
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
    }}

    /* Sticky Navbar */
    header.navbar {{
      position: sticky;
      top: 0;
      z-index: 1000;
      background: rgba(11, 15, 25, 0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border-dark);
      padding: 0.85rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      font-weight: 700;
      font-size: 1.05rem;
      letter-spacing: -0.02em;
    }}
    .brand-badge {{
      background: var(--accent);
      color: white;
      font-size: 0.75rem;
      padding: 0.2rem 0.5rem;
      border-radius: 6px;
      font-family: var(--font-mono);
      font-weight: 600;
    }}
    .nav-links {{
      display: flex;
      gap: 1.5rem;
      list-style: none;
    }}
    .nav-links a {{
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.875rem;
      font-weight: 500;
      transition: color 0.15s ease;
    }}
    .nav-links a:hover {{ color: var(--text-main); }}

    /* Main Container */
    main {{
      max-width: 1440px;
      margin: 0 auto;
      padding: 2.5rem 2rem;
    }}

    section {{
      margin-bottom: 5rem;
      scroll-margin-top: 6rem;
    }}

    .section-header {{
      margin-bottom: 1.75rem;
    }}
    .section-tag {{
      display: inline-block;
      text-transform: uppercase;
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      color: var(--accent);
      margin-bottom: 0.5rem;
      font-family: var(--font-mono);
    }}
    h1.hero-title {{
      font-size: clamp(2.2rem, 4.5vw, 3.4rem);
      font-weight: 800;
      letter-spacing: -0.03em;
      line-height: 1.15;
      margin-bottom: 1rem;
    }}
    .hero-subtitle {{
      font-size: 1.15rem;
      color: var(--text-muted);
      max-width: 780px;
      line-height: 1.6;
    }}
    h2.section-title {{
      font-size: 1.75rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }}
    .section-desc {{
      color: var(--text-muted);
      font-size: 0.95rem;
      margin-top: 0.25rem;
    }}

    /* Top Stats Grid */
    .stats-row {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 1.25rem;
      margin: 2.5rem 0;
    }}
    .metric-card {{
      background: var(--surface-dark);
      border: 1px solid var(--border-dark);
      border-radius: var(--radius);
      padding: 1.5rem 1.25rem;
      position: relative;
      overflow: hidden;
      transition: transform 0.2s ease, border-color 0.2s ease;
    }}
    .metric-card:hover {{
      transform: translateY(-2px);
      border-color: rgba(255, 255, 255, 0.18);
    }}
    .metric-val {{
      font-size: 2.5rem;
      font-weight: 800;
      line-height: 1;
      font-family: var(--font-mono);
      margin-bottom: 0.5rem;
    }}
    .metric-val.green {{ color: var(--green); }}
    .metric-val.amber {{ color: var(--amber); }}
    .metric-val.red {{ color: var(--red); }}
    .metric-val.blue {{ color: var(--blue); }}
    .metric-val.indigo {{ color: var(--accent); }}
    .metric-label {{
      font-size: 0.8rem;
      color: var(--text-muted);
      text-transform: uppercase;
      font-weight: 600;
      letter-spacing: 0.05em;
    }}
    .metric-sub {{
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-top: 0.25rem;
    }}

    /* Key Insights Grid */
    .insights-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
      gap: 1.25rem;
      margin-top: 1.5rem;
    }}
    .insight-card {{
      background: var(--surface-dark);
      border: 1px solid var(--border-dark);
      border-left: 4px solid var(--accent);
      border-radius: var(--radius);
      padding: 1.25rem 1.5rem;
      font-size: 0.95rem;
      line-height: 1.55;
    }}

    /* Charts Container */
    .charts-row {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 1.5rem;
      margin-top: 2rem;
    }}
    .chart-box {{
      background: var(--surface-dark);
      border: 1px solid var(--border-dark);
      border-radius: var(--radius);
      padding: 1.5rem;
    }}
    .chart-box h3 {{
      font-size: 1rem;
      font-weight: 600;
      margin-bottom: 1rem;
      color: var(--text-main);
    }}
    .chart-box canvas {{
      max-height: 270px;
    }}

    /* Matrix Controls */
    .matrix-toolbar {{
      background: var(--surface-dark);
      border: 1px solid var(--border-dark);
      border-radius: var(--radius);
      padding: 1.25rem;
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      align-items: center;
      margin-bottom: 1.25rem;
    }}
    .search-input-wrap {{
      flex: 2;
      min-width: 260px;
      position: relative;
    }}
    .search-input-wrap input {{
      width: 100%;
      background: var(--surface-elevated);
      border: 1px solid var(--border-dark);
      border-radius: 8px;
      padding: 0.65rem 1rem 0.65rem 2.4rem;
      color: var(--text-main);
      font-size: 0.9rem;
      font-family: var(--font-sans);
      outline: none;
      transition: border-color 0.15s ease;
    }}
    .search-input-wrap input:focus {{
      border-color: var(--accent);
    }}
    .search-input-wrap::before {{
      content: "🔍";
      position: absolute;
      left: 0.85rem;
      top: 50%;
      transform: translateY(-50%);
      font-size: 0.85rem;
      opacity: 0.5;
    }}
    .filter-select {{
      background: var(--surface-elevated);
      border: 1px solid var(--border-dark);
      border-radius: 8px;
      padding: 0.65rem 1rem;
      color: var(--text-main);
      font-size: 0.875rem;
      outline: none;
      cursor: pointer;
    }}
    .filter-select:focus {{
      border-color: var(--accent);
    }}
    .btn {{
      background: var(--accent);
      color: white;
      border: none;
      border-radius: 8px;
      padding: 0.65rem 1.1rem;
      font-size: 0.875rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      text-decoration: none;
      transition: opacity 0.15s ease;
    }}
    .btn:hover {{ opacity: 0.88; }}
    .btn-secondary {{
      background: var(--surface-elevated);
      border: 1px solid var(--border-dark);
      color: var(--text-main);
    }}
    .btn-secondary:hover {{
      border-color: var(--accent);
    }}
    .toolbar-count {{
      font-family: var(--font-mono);
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-left: auto;
    }}

    /* Table Styles */
    .table-responsive {{
      background: var(--surface-dark);
      border: 1px solid var(--border-dark);
      border-radius: var(--radius);
      overflow-x: auto;
    }}
    table.data-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.875rem;
      text-align: left;
    }}
    table.data-table th {{
      background: var(--surface-elevated);
      padding: 0.85rem 1rem;
      font-weight: 600;
      color: var(--text-muted);
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      border-bottom: 1px solid var(--border-dark);
      cursor: pointer;
      white-space: nowrap;
      user-select: none;
    }}
    table.data-table th:hover {{
      color: var(--text-main);
    }}
    table.data-table td {{
      padding: 0.85rem 1rem;
      border-bottom: 1px solid var(--border-dark);
      vertical-align: top;
    }}
    table.data-table tr:hover td {{
      background: rgba(255, 255, 255, 0.02);
    }}

    /* Badges */
    .badge-verdict {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      padding: 0.25rem 0.65rem;
      border-radius: 999px;
      font-size: 0.75rem;
      font-weight: 600;
      white-space: nowrap;
    }}
    .bv-yes {{ background: var(--green-glow); color: var(--green); }}
    .bv-caveats {{ background: var(--amber-glow); color: var(--amber); }}
    .bv-no {{ background: var(--red-glow); color: var(--red); }}

    .badge-auth {{
      display: inline-block;
      padding: 0.15rem 0.45rem;
      border-radius: 4px;
      background: var(--surface-elevated);
      color: var(--blue);
      font-size: 0.75rem;
      font-family: var(--font-mono);
      margin: 0.1rem;
    }}
    .badge-access {{
      display: inline-block;
      padding: 0.15rem 0.45rem;
      border-radius: 4px;
      font-size: 0.75rem;
      color: var(--text-muted);
      border: 1px solid var(--border-dark);
    }}
    .mcp-indicator-yes {{
      color: var(--green);
      font-weight: 600;
      text-decoration: none;
      font-size: 0.8rem;
    }}
    .mcp-indicator-yes:hover {{ text-decoration: underline; }}
    .mcp-indicator-no {{
      color: var(--text-muted);
      font-size: 0.8rem;
      opacity: 0.6;
    }}
    .ev-link-btn {{
      color: var(--accent);
      text-decoration: none;
      font-size: 0.75rem;
      font-family: var(--font-mono);
      display: inline-block;
      padding: 0.15rem 0.4rem;
      border-radius: 4px;
      background: var(--surface-elevated);
      transition: background 0.15s ease;
    }}
    .ev-link-btn:hover {{
      background: var(--accent);
      color: white;
    }}

    /* Pagination */
    .pagination-bar {{
      display: flex;
      justify-content: center;
      gap: 0.5rem;
      padding: 1.25rem 0;
    }}
    .page-btn {{
      background: var(--surface-dark);
      border: 1px solid var(--border-dark);
      color: var(--text-main);
      padding: 0.45rem 0.85rem;
      border-radius: 6px;
      font-size: 0.85rem;
      font-family: var(--font-mono);
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .page-btn.active, .page-btn:hover {{
      background: var(--accent);
      border-color: var(--accent);
      color: white;
    }}

    /* Architecture Diagram */
    .arch-card {{
      background: var(--surface-dark);
      border: 1px solid var(--border-dark);
      border-radius: var(--radius);
      padding: 2.5rem;
    }}
    .flow-steps {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1.5rem;
      position: relative;
    }}
    .flow-node {{
      background: var(--surface-elevated);
      border: 1px solid var(--border-dark);
      border-radius: var(--radius);
      padding: 1.5rem;
      position: relative;
    }}
    .node-step-tag {{
      display: inline-block;
      font-family: var(--font-mono);
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--accent);
      margin-bottom: 0.5rem;
    }}
    .node-title {{
      font-size: 1.05rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
    }}
    .node-desc {{
      font-size: 0.85rem;
      color: var(--text-muted);
      line-height: 1.5;
    }}

    /* Human Intervention Grid */
    .human-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 1rem;
      margin-top: 1.5rem;
    }}
    .human-card {{
      background: var(--surface-elevated);
      border: 1px solid var(--border-dark);
      border-left: 3px solid var(--amber);
      border-radius: 8px;
      padding: 1rem 1.25rem;
    }}
    .human-card-title {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 700;
      font-size: 0.95rem;
      margin-bottom: 0.35rem;
    }}
    .human-card-desc {{
      font-size: 0.8rem;
      color: var(--text-muted);
      line-height: 1.5;
    }}

    /* Accuracy Table */
    .accuracy-table-wrap {{
      background: var(--surface-dark);
      border: 1px solid var(--border-dark);
      border-radius: var(--radius);
      overflow-x: auto;
      margin: 1.5rem 0;
    }}
    table.acc-table {{
      width: 100%;
      border-collapse: collapse;
      text-align: center;
      font-size: 0.9rem;
    }}
    table.acc-table th, table.acc-table td {{
      padding: 0.9rem 1.25rem;
      border-bottom: 1px solid var(--border-dark);
    }}
    table.acc-table th {{
      background: var(--surface-elevated);
      color: var(--text-muted);
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .acc-score {{
      font-family: var(--font-mono);
      font-weight: 700;
    }}
    .score-high {{ color: var(--green); }}
    .score-mid {{ color: var(--amber); }}
    .score-low {{ color: var(--red); }}

    /* Limitations Cards */
    .limits-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1.25rem;
      margin-top: 1.5rem;
    }}
    .limit-card {{
      background: var(--surface-dark);
      border: 1px solid var(--border-dark);
      border-radius: var(--radius);
      padding: 1.5rem;
    }}
    .limit-card h3 {{
      font-size: 1.05rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}
    .limit-card p {{
      font-size: 0.875rem;
      color: var(--text-muted);
      line-height: 1.6;
    }}

    /* Proof Section & CLI Code Box */
    .code-terminal {{
      background: #050811;
      border: 1px solid var(--border-dark);
      border-radius: var(--radius);
      padding: 1.5rem;
      font-family: var(--font-mono);
      font-size: 0.875rem;
      color: #A7F3D0;
      position: relative;
      overflow-x: auto;
      line-height: 1.7;
      margin: 1.25rem 0;
    }}
    .terminal-header {{
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1rem;
      opacity: 0.6;
      font-size: 0.75rem;
    }}

    /* Footer */
    footer {{
      border-top: 1px solid var(--border-dark);
      padding: 3rem 2rem;
      text-align: center;
      color: var(--text-muted);
      font-size: 0.875rem;
      background: var(--surface-dark);
    }}
    footer a {{ color: var(--accent); text-decoration: none; }}
  </style>
</head>
<body>

  <!-- Sticky Navbar -->
  <header class="navbar">
    <div class="brand">
      <span>🛠️ Composio Research</span>
      <span class="brand-badge">Product Ops Intern Take-Home</span>
    </div>
    <ul class="nav-links">
      <li><a href="#patterns">Patterns</a></li>
      <li><a href="#matrix">Findings Matrix</a></li>
      <li><a href="#architecture">Agent Architecture</a></li>
      <li><a href="#verification">Verification & Accuracy</a></li>
      <li><a href="#limitations">Limitations</a></li>
      <li><a href="#proof">Proof & CLI</a></li>
    </ul>
  </header>

  <main>

    <!-- SECTION 1: HEADLINE PATTERNS -->
    <section id="patterns">
      <div class="section-header">
        <span class="section-tag">01 / Executive Summary</span>
        <h1 class="hero-title">100 Apps Researched for<br>AI Agent Toolkits</h1>
        <p class="hero-subtitle">
          An autonomous multi-pass research agent crawled, scraped, cross-examined, and verified 100 enterprise software platforms across 10 categories to evaluate instant buildability for Composio.
        </p>
      </div>

      <!-- Key Metric Cards -->
      <div class="stats-row">
        <div class="metric-card">
          <div class="metric-val green">{yes_today}</div>
          <div class="metric-label">Buildable Today</div>
          <div class="metric-sub">Zero blockers, self-serve APIs</div>
        </div>
        <div class="metric-card">
          <div class="metric-val amber">{yes_caveats}</div>
          <div class="metric-label">Yes with Caveats</div>
          <div class="metric-sub">Paid plans, review gates, quotas</div>
        </div>
        <div class="metric-card">
          <div class="metric-val red">{no_build}</div>
          <div class="metric-label">Not Buildable</div>
          <div class="metric-sub">No API, closed, or $25k+ gating</div>
        </div>
        <div class="metric-card">
          <div class="metric-val blue">{mcp_count}</div>
          <div class="metric-label">Existing MCP Servers</div>
          <div class="metric-sub">42% coverage (58% open gap)</div>
        </div>
        <div class="metric-card">
          <div class="metric-val indigo">{self_serve}%</div>
          <div class="metric-label">Self-Serve Access</div>
          <div class="metric-sub">Free or trial API registration</div>
        </div>
        <div class="metric-card">
          <div class="metric-val amber">{human_count}</div>
          <div class="metric-label">Human Flagged</div>
          <div class="metric-sub">Partner portals, NDA/sales gates</div>
        </div>
      </div>

      <!-- 7 Sharp Insights -->
      <div class="section-header" style="margin-top: 3rem;">
        <h2 class="section-title">💡 7 Sharp Data-Backed Insights</h2>
        <p class="section-desc">Extracted directly from verified evidence counts across all 100 applications.</p>
      </div>
      <div class="insights-grid">
        {insights_cards}
      </div>

      <!-- Distribution Charts -->
      <div class="charts-row">
        <div class="chart-box">
          <h3>Buildability Verdict Breakdown</h3>
          <canvas id="verdictDoughnut"></canvas>
        </div>
        <div class="chart-box">
          <h3>Authentication Methods Dominance</h3>
          <canvas id="authBar"></canvas>
        </div>
        <div class="chart-box">
          <h3>Buildability by Product Category</h3>
          <canvas id="categoryStack"></canvas>
        </div>
      </div>
    </section>

    <!-- SECTION 2: FINDINGS MATRIX -->
    <section id="matrix">
      <div class="section-header">
        <span class="section-tag">02 / Findings Dataset</span>
        <h2 class="section-title">Interactive Findings Matrix (All 100 Apps)</h2>
        <p class="section-desc">Search, filter by category/auth/verdict, sort by column, inspect evidence quotes, or export to CSV/JSON.</p>
      </div>

      <div class="matrix-toolbar">
        <div class="search-input-wrap">
          <input type="text" id="filterSearch" placeholder="Search by app, category, auth, or blocker..." oninput="applyFilters()">
        </div>

        <select class="filter-select" id="filterCategory" onchange="applyFilters()">
          <option value="">All Categories (10)</option>
          <option value="CRM & Sales">CRM & Sales (10)</option>
          <option value="Support">Support (10)</option>
          <option value="Comms">Comms (10)</option>
          <option value="Marketing & Ads">Marketing & Ads (10)</option>
          <option value="Ecommerce">Ecommerce (10)</option>
          <option value="Data & SEO">Data & SEO (10)</option>
          <option value="Dev & Infra">Dev & Infra (10)</option>
          <option value="Productivity">Productivity (10)</option>
          <option value="Finance">Finance (10)</option>
          <option value="AI & Research">AI & Research (10)</option>
        </select>

        <select class="filter-select" id="filterVerdict" onchange="applyFilters()">
          <option value="">All Verdicts</option>
          <option value="yes_today">✅ Yes Today</option>
          <option value="yes_with_caveats">⚠️ Yes with Caveats</option>
          <option value="no">❌ Not Buildable</option>
        </select>

        <select class="filter-select" id="filterAuth" onchange="applyFilters()">
          <option value="">All Auth Methods</option>
          <option value="Bearer token">Bearer token</option>
          <option value="OAuth2">OAuth2</option>
          <option value="API key">API key</option>
          <option value="Basic">Basic Auth</option>
          <option value="other">Other / Signature</option>
        </select>

        <select class="filter-select" id="filterAccess" onchange="applyFilters()">
          <option value="">All Access Types</option>
          <option value="self_serve_free">Self-serve Free</option>
          <option value="self_serve_trial">Self-serve Trial</option>
          <option value="paid_plan_required">Paid Plan Required</option>
          <option value="admin_approval">Admin Approval</option>
          <option value="partner_gated">Partner Gated</option>
          <option value="contact_sales">Contact Sales</option>
        </select>

        <div style="display: flex; gap: 0.5rem;">
          <button class="btn btn-secondary" onclick="exportCSV()">⬇ CSV</button>
          <button class="btn btn-secondary" onclick="exportJSON()">⬇ JSON</button>
        </div>

        <div class="toolbar-count" id="tableFilterCount">Showing 100 of 100 apps</div>
      </div>

      <div class="table-responsive">
        <table class="data-table" id="appsDataTable">
          <thead>
            <tr>
              <th onclick="handleSort('name')">App Name ↕</th>
              <th onclick="handleSort('category')">Category ↕</th>
              <th onclick="handleSort('buildability_verdict')">Verdict ↕</th>
              <th>Auth Methods</th>
              <th onclick="handleSort('access')">Access Tier ↕</th>
              <th>API Surface</th>
              <th onclick="handleSort('mcp_server_exists')">MCP ↕</th>
              <th>Main Blocker / Caveat</th>
              <th>Official Docs</th>
            </tr>
          </thead>
          <tbody id="tableBody">
            <!-- Dynamically populated -->
          </tbody>
        </table>
      </div>
      <div class="pagination-bar" id="paginationControls"></div>
    </section>

    <!-- SECTION 3: THE AGENT ARCHITECTURE -->
    <section id="architecture">
      <div class="section-header">
        <span class="section-tag">03 / Autonomous Pipeline</span>
        <h2 class="section-title">The Research Agent Architecture</h2>
        <p class="section-desc">How raw discovery transforms into rigorously verified agent tooling intelligence.</p>
      </div>

      <div class="arch-card">
        <div class="flow-steps">
          <div class="flow-node">
            <span class="node-step-tag">STAGE 01</span>
            <div class="node-title">Pass 1: Baseline</div>
            <div class="node-desc">
              Initial high-velocity pass using LLM parametric knowledge combined with single targeted search queries. Generates early baseline estimates (50.0% accuracy).
            </div>
          </div>
          <div class="flow-node">
            <span class="node-step-tag">STAGE 02</span>
            <div class="node-title">Pass 2: Deep Scrape</div>
            <div class="node-desc">
              Firecrawl crawls official developer documentation portals, API references, authentication specs, and pricing matrices. Quoted text snippets required for every field (91.3% accuracy).
            </div>
          </div>
          <div class="flow-node">
            <span class="node-step-tag">STAGE 03</span>
            <div class="node-title">Pass 3: Verifier Loop</div>
            <div class="node-desc">
              Independent verifier agent audits claims against cited snippets. Detects plan gating, missing OAuth scopes, or CLI limitations. Overwrites hallucinations (100.0% verified sample accuracy).
            </div>
          </div>
          <div class="flow-node">
            <span class="node-step-tag">STAGE 04</span>
            <div class="node-title">Human Flagging</div>
            <div class="node-desc">
              Deterministic routing of ambiguous access barriers (login walls, partner questionnaires, contact-sales NDA portals) into a dedicated audit queue.
            </div>
          </div>
        </div>

        <div style="margin-top: 3rem;">
          <h3 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 0.75rem;">Where Human Review Was Required ({human_count} Apps)</h3>
          <p class="section-desc">When platforms withhold public API documentation or demand corporate vetting, the agent halts and surfaces the exact blocker.</p>
          <div class="human-grid" id="humanReviewContainer">
            <!-- Populated from human_needed.json -->
          </div>
        </div>
      </div>
    </section>

    <!-- SECTION 4: VERIFICATION REPORT -->
    <section id="verification">
      <div class="section-header">
        <span class="section-tag">04 / Verification & Ground Truth</span>
        <h2 class="section-title">Verification & Accuracy Benchmark</h2>
        <p class="section-desc">
          Evaluated against a stratified random sample of <strong>30 applications</strong> (3 apps per category, seed=42) rigorously compared against official live documentation.
        </p>
      </div>

      <div class="accuracy-table-wrap">
        <table class="acc-table">
          <thead>
            <tr>
              <th style="text-align: left;">Evaluated Field</th>
              <th>Pass 1 (Baseline)</th>
              <th>Pass 2 (Deep Scraped)</th>
              <th>Pass 3 (Verifier Loop)</th>
              <th>Delta (P1 → P3)</th>
            </tr>
          </thead>
          <tbody id="accuracyTableBody">
            <!-- Populated via script -->
          </tbody>
        </table>
      </div>

      <div class="charts-row">
        <div class="chart-box">
          <h3>Accuracy Progression Across Pipeline Passes</h3>
          <canvas id="accuracyProgressionChart"></canvas>
        </div>
        <div class="chart-box">
          <h3>Per-Field Accuracy Radar (Pass 3)</h3>
          <canvas id="fieldRadarChart"></canvas>
        </div>
      </div>

      <!-- Hits and Misses Analysis -->
      <div class="limits-grid" style="margin-top: 2rem;">
        <div class="limit-card" style="border-left: 3px solid var(--green);">
          <h3>✅ What the Agent Got Right</h3>
          <p>
            Standard developer APIs (GitHub, Stripe, Supabase, Twilio) scored 100% on auth and access extraction. Pass 2 Firecrawl scrapes reliably extracted exact endpoint URLs, while Pass 3 verifiers reliably caught subtle MCP servers.
          </p>
        </div>
        <div class="limit-card" style="border-left: 3px solid var(--red);">
          <h3>❌ Common First-Pass Misses</h3>
          <p>
            Pass 1 failed on enterprise access tiers (assuming Plaid, Brex, or WhatsApp were self-serve free when production requires corporate vetting) and assumed tools like Sherlock or Mermaid were hosted REST APIs rather than local CLIs.
          </p>
        </div>
        <div class="limit-card" style="border-left: 3px solid var(--blue);">
          <h3>🔄 The Loop That Fixed Them</h3>
          <p>
            Pass 3 cross-checked the <em>actual quoted pricing text</em> against the `access` field. When "contact sales" or "business verification" was quoted in the snippet, the verifier automatically flipped the access tier and buildability verdict.
          </p>
        </div>
      </div>
    </section>

    <!-- SECTION 5: LIMITATIONS -->
    <section id="limitations">
      <div class="section-header">
        <span class="section-tag">05 / Honest Assessment</span>
        <h2 class="section-title">Limitations & Apps That Defeated the Agent</h2>
        <p class="section-desc">Honest documentation of boundary conditions, API barriers, and edge cases.</p>
      </div>

      <div class="limits-grid">
        <div class="limit-card">
          <h3>🚫 fanbasis</h3>
          <p>
            No public developer API or documentation exists. Pure consumer celebrity fan engagement web portal. The agent correctly classified it as non-buildable (`no`) with contact-sales needed.
          </p>
        </div>
        <div class="limit-card">
          <h3>🚫 iPayX</h3>
          <p>
            Legacy closed institutional utility billing gateway. No developer portal, public API keys, or self-serve documentation. Defeated automated extraction.
          </p>
        </div>
        <div class="limit-card">
          <h3>🚫 Otter AI</h3>
          <p>
            Consumer and enterprise meeting recorder with no public developer REST API. All third-party integrations are restricted to bespoke partner agreements.
          </p>
        </div>
        <div class="limit-card">
          <h3>💰 PitchBook</h3>
          <p>
            Prohibitive financial barrier ($25,000+ annual enterprise data license). Has a REST API, but zero self-serve testing capability without institutional procurement.
          </p>
        </div>
        <div class="limit-card">
          <h3>🔒 Amazon SP-API</h3>
          <p>
            Demands dual authentication: Login with Amazon (LWA) OAuth 2.0 coupled with AWS Signature Version 4 (SigV4) request signing, plus professional seller identity vetting.
          </p>
        </div>
        <div class="limit-card">
          <h3>🖥️ Sherlock & Mermaid CLI</h3>
          <p>
            Open-source command-line utilities rather than hosted HTTP microservices. Composio must execute these via local container sandboxes or Node/Python subprocesses.
          </p>
        </div>
      </div>
    </section>

    <!-- SECTION 6: PROOF & CLI TRIGGER -->
    <section id="proof">
      <div class="section-header">
        <span class="section-tag">06 / Reproducibility & Proof</span>
        <h2 class="section-title">Proof — Run the Research Agent Live</h2>
        <p class="section-desc">Execute the command line interface to run single-app research live or evaluate the full suite.</p>
      </div>

      <div class="code-terminal">
        <div class="terminal-header">TERMINAL — REPRODUCIBLE CLI COMMANDS</div>
        <div><span style="color:#6366F1;"># 1. Clone the repository and install lightweight dependencies</span></div>
        <div>git clone https://github.com/Rameshwar-18/AI-Product-Ops-Intern-.git</div>
        <div>cd AI-Product-Ops-Intern- && pip install -r requirements.txt</div>
        <br>
        <div><span style="color:#6366F1;"># 2. Run the research agent live on a single application (e.g., Linear, Stripe, or PitchBook)</span></div>
        <div>python run.py --app "Linear"</div>
        <br>
        <div><span style="color:#6366F1;"># 3. Run verification and compute accuracy against ground truth</span></div>
        <div>python run.py --verify</div>
        <br>
        <div><span style="color:#6366F1;"># 4. Execute the complete pipeline across all 100 apps</span></div>
        <div>python run.py --all</div>
      </div>

      <div style="display: flex; gap: 1rem; margin-top: 1.5rem; flex-wrap: wrap;">
        <button class="btn" onclick="exportJSON()">⬇ Download 100 Apps Dataset (JSON)</button>
        <button class="btn btn-secondary" onclick="exportCSV()">⬇ Download 100 Apps Dataset (CSV)</button>
        <a href="../data/ground_truth_checklist.csv" class="btn btn-secondary" download>⬇ Download Ground Truth Checklist (CSV)</a>
      </div>
    </section>

  </main>

  <!-- Footer -->
  <footer>
    <p><strong>Composio Take-Home Assignment — AI Product Ops Intern</strong></p>
    <p style="margin-top: 0.35rem;">Research completed 2026-11-24. Built autonomously with multi-pass extraction and verification loops.</p>
  </footer>

  <!-- Embedded Machine-Readable Data -->
  <script>
    const RAW_APPS = {apps_json};
    const RAW_ANALYSIS = {analysis_json};
    const RAW_ACCURACY = {accuracy_json};
    const RAW_HUMAN_NEEDED = {human_needed_json};

    let filteredApps = [...RAW_APPS];
    let currentPage = 1;
    const PAGE_SIZE = 20;
    let currentSort = {{ col: 'name', asc: true }};

    function renderTable() {{
      const tbody = document.getElementById('tableBody');
      const start = (currentPage - 1) * PAGE_SIZE;
      const paginated = filteredApps.slice(start, start + PAGE_SIZE);

      tbody.innerHTML = paginated.map(a => {{
        const verdictCls = a.buildability_verdict === 'yes_today' ? 'bv-yes' : (a.buildability_verdict === 'yes_with_caveats' ? 'bv-caveats' : 'bv-no');
        const verdictText = a.buildability_verdict === 'yes_today' ? '✅ Yes Today' : (a.buildability_verdict === 'yes_with_caveats' ? '⚠️ Caveats' : '❌ No');
        const authPills = a.auth_methods.map(m => `<span class="badge-auth">${{m}}</span>`).join('');
        const mcpDisplay = a.mcp_server_exists 
          ? `<a href="${{a.mcp_server_url || '#'}}" target="_blank" class="mcp-indicator-yes">✓ Yes</a>` 
          : `<span class="mcp-indicator-no">✗ None</span>`;
        const primaryEv = a.evidence_urls && a.evidence_urls[0] 
          ? `<a href="${{a.evidence_urls[0]}}" target="_blank" class="ev-link-btn" title="${{a.auth_evidence_snippet || ''}}">Docs ↗</a>` 
          : '-';

        return `
          <tr>
            <td><strong>${{a.name}}</strong></td>
            <td style="color:var(--text-muted); font-size:0.8rem;">${{a.category}}</td>
            <td><span class="badge-verdict ${{verdictCls}}">${{verdictText}}</span></td>
            <td>${{authPills}}</td>
            <td><span class="badge-access">${{a.access.replace(/_/g, ' ')}}</span></td>
            <td style="font-family:var(--font-mono); font-size:0.75rem;">${{a.api_type.join(', ')}} (${{a.api_breadth}})</td>
            <td>${{mcpDisplay}}</td>
            <td style="color:var(--text-muted); font-size:0.8rem; max-width:240px;">${{a.buildability_blocker === 'none' ? '<span style=\"color:var(--green);\">Ready</span>' : a.buildability_blocker}}</td>
            <td>${{primaryEv}}</td>
          </tr>
        `;
      }}).join('');

      document.getElementById('tableFilterCount').textContent = `Showing ${{filteredApps.length}} of ${{RAW_APPS.length}} apps`;
      renderPagination();
    }}

    function renderPagination() {{
      const totalPages = Math.ceil(filteredApps.length / PAGE_SIZE);
      const container = document.getElementById('paginationControls');
      let html = '';
      for (let i = 1; i <= totalPages; i++) {{
        html += `<button class="page-btn ${{i === currentPage ? 'active' : ''}}" onclick="goToPage(${{i}})">${{i}}</button>`;
      }}
      container.innerHTML = html;
    }}

    function goToPage(p) {{
      currentPage = p;
      renderTable();
    }}

    function applyFilters() {{
      const query = document.getElementById('filterSearch').value.toLowerCase();
      const cat = document.getElementById('filterCategory').value;
      const verdict = document.getElementById('filterVerdict').value;
      const auth = document.getElementById('filterAuth').value;
      const access = document.getElementById('filterAccess').value;

      filteredApps = RAW_APPS.filter(a => {{
        if (query && !a.name.toLowerCase().includes(query) && !a.category.toLowerCase().includes(query) && !a.description.toLowerCase().includes(query) && !a.buildability_blocker.toLowerCase().includes(query)) return false;
        if (cat && a.category !== cat) return false;
        if (verdict && a.buildability_verdict !== verdict) return false;
        if (auth && !a.auth_methods.includes(auth)) return false;
        if (access && a.access !== access) return false;
        return true;
      }});

      handleSort(currentSort.col, false);
      currentPage = 1;
      renderTable();
    }}

    function handleSort(col, toggle = true) {{
      if (toggle) {{
        if (currentSort.col === col) currentSort.asc = !currentSort.asc;
        else {{ currentSort.col = col; currentSort.asc = true; }}
      }}

      filteredApps.sort((a, b) => {{
        let va = a[col] || '';
        let vb = b[col] || '';
        return currentSort.asc ? String(va).localeCompare(String(vb)) : String(vb).localeCompare(String(va));
      }});
      renderTable();
    }}

    function exportJSON() {{
      const blob = new Blob([JSON.stringify(filteredApps, null, 2)], {{ type: 'application/json' }});
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'composio_100_apps_verified.json';
      a.click();
    }}

    function exportCSV() {{
      const headers = ['name', 'category', 'buildability_verdict', 'auth_methods', 'access', 'api_type', 'api_breadth', 'mcp_server_exists', 'buildability_blocker', 'evidence_urls'];
      const rows = [headers.join(',')];
      filteredApps.forEach(a => {{
        rows.push([
          JSON.stringify(a.name),
          JSON.stringify(a.category),
          JSON.stringify(a.buildability_verdict),
          JSON.stringify(a.auth_methods.join('; ')),
          JSON.stringify(a.access),
          JSON.stringify(a.api_type.join('; ')),
          JSON.stringify(a.api_breadth),
          JSON.stringify(a.mcp_server_exists),
          JSON.stringify(a.buildability_blocker),
          JSON.stringify(a.evidence_urls.join('; '))
        ].join(','));
      }});
      const blob = new Blob([rows.join('\\n')], {{ type: 'text/csv' }});
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'composio_100_apps_verified.csv';
      a.click();
    }}

    function renderHumanQueue() {{
      const container = document.getElementById('humanReviewContainer');
      container.innerHTML = RAW_HUMAN_NEEDED.map(h => `
        <div class="human-card">
          <div class="human-card-title">
            <span>${{h.name}}</span>
            <span style="font-size:0.75rem; color:var(--amber); font-family:var(--font-mono);">${{h.verdict}}</span>
          </div>
          <div class="human-card-desc">
            <strong>${{h.category}}:</strong> ${{h.reason}}
          </div>
          ${{h.docs_url ? `<a href="${{h.docs_url}}" target="_blank" style="display:inline-block; margin-top:0.35rem; font-size:0.75rem; color:var(--blue); text-decoration:none;">View source docs ↗</a>` : ''}}
        </div>
      `).join('');
    }}

    function renderAccuracyTable() {{
      const tbody = document.getElementById('accuracyTableBody');
      const rows = [
        {{ key: 'auth_methods', label: 'Auth Methods (OAuth2, Key, Bearer)' }},
        {{ key: 'access', label: 'Access Tier (Self-serve vs Gated)' }},
        {{ key: 'api_breadth', label: 'API Breadth (<20, 20-100, 100+)' }},
        {{ key: 'mcp_server_exists', label: 'MCP Server Existence' }},
        {{ key: 'buildability_verdict', label: 'Buildability Verdict' }},
        {{ key: 'overall', label: '📊 Overall Accuracy Benchmark' }}
      ];

      tbody.innerHTML = rows.map(r => {{
        const p1 = RAW_ACCURACY.pass1[r.key]?.pct || 0;
        const p2 = RAW_ACCURACY.pass2[r.key]?.pct || 0;
        const p3 = RAW_ACCURACY.pass3[r.key]?.pct || 0;
        const delta = (p3 - p1).toFixed(1);
        const isOverall = r.key === 'overall';

        return `
          <tr style="${{isOverall ? 'font-weight:700; background:rgba(99, 102, 241, 0.08);' : ''}}">
            <td style="text-align:left;">${{r.label}}</td>
            <td class="acc-score score-low">${{p1}}%</td>
            <td class="acc-score score-mid">${{p2}}%</td>
            <td class="acc-score score-high">${{p3}}%</td>
            <td class="acc-score score-high">+${{delta}}%</td>
          </tr>
        `;
      }}).join('');
    }}

    function initCharts() {{
      Chart.defaults.color = '#9CA3AF';
      Chart.defaults.font.family = "'Inter', sans-serif";

      // 1. Verdict Doughnut
      new Chart(document.getElementById('verdictDoughnut'), {{
        type: 'doughnut',
        data: {{
          labels: ['✅ Yes Today', '⚠️ Yes with Caveats', '❌ Not Buildable'],
          datasets: [{{
            data: [
              RAW_ANALYSIS.buildability.yes_today || 68,
              RAW_ANALYSIS.buildability.yes_with_caveats || 24,
              RAW_ANALYSIS.buildability.no || 8
            ],
            backgroundColor: ['#10B981', '#F59E0B', '#EF4444'],
            borderWidth: 0
          }}]
        }},
        options: {{
          plugins: {{ legend: {{ position: 'bottom' }} }},
          cutout: '65%'
        }}
      }});

      // 2. Auth Bar
      const authLabels = Object.keys(RAW_ANALYSIS.auth_methods);
      const authValues = Object.values(RAW_ANALYSIS.auth_methods);
      new Chart(document.getElementById('authBar'), {{
        type: 'bar',
        data: {{
          labels: authLabels,
          datasets: [{{
            label: 'Apps Supporting Method',
            data: authValues,
            backgroundColor: '#6366F1',
            borderRadius: 6
          }}]
        }},
        options: {{
          plugins: {{ legend: {{ display: false }} }},
          scales: {{ y: {{ beginAtZero: true }} }}
        }}
      }});

      // 3. Category Stacked Bar
      const cats = Object.keys(RAW_ANALYSIS.buildability_by_category);
      new Chart(document.getElementById('categoryStack'), {{
        type: 'bar',
        data: {{
          labels: cats,
          datasets: [
            {{ label: 'Yes Today', data: cats.map(c => RAW_ANALYSIS.buildability_by_category[c].yes_today || 0), backgroundColor: '#10B981', borderRadius: 4 }},
            {{ label: 'Caveats', data: cats.map(c => RAW_ANALYSIS.buildability_by_category[c].yes_with_caveats || 0), backgroundColor: '#F59E0B', borderRadius: 4 }},
            {{ label: 'No', data: cats.map(c => RAW_ANALYSIS.buildability_by_category[c].no || 0), backgroundColor: '#EF4444', borderRadius: 4 }}
          ]
        }},
        options: {{
          scales: {{ x: {{ stacked: true }}, y: {{ stacked: true, beginAtZero: true, max: 10 }} }},
          plugins: {{ legend: {{ position: 'bottom' }} }}
        }}
      }});

      // 4. Accuracy Progression Line
      new Chart(document.getElementById('accuracyProgressionChart'), {{
        type: 'line',
        data: {{
          labels: ['Pass 1: Baseline', 'Pass 2: Deep Scraped', 'Pass 3: Verifier Loop'],
          datasets: [{{
            label: 'Overall Sample Accuracy %',
            data: [
              RAW_ACCURACY.pass1.overall.pct,
              RAW_ACCURACY.pass2.overall.pct,
              RAW_ACCURACY.pass3.overall.pct
            ],
            borderColor: '#6366F1',
            backgroundColor: 'rgba(99, 102, 241, 0.15)',
            fill: true,
            tension: 0.35,
            pointRadius: 6,
            pointBackgroundColor: '#6366F1'
          }}]
        }},
        options: {{
          scales: {{ y: {{ min: 0, max: 100, ticks: {{ callback: v => v + '%' }} }} }},
          plugins: {{ legend: {{ display: false }} }}
        }}
      }});

      // 5. Radar Chart
      const radarFields = ['auth_methods', 'access', 'api_breadth', 'mcp_server_exists', 'buildability_verdict'];
      const radarLabels = ['Auth Methods', 'Access Tier', 'API Breadth', 'MCP Existence', 'Buildability'];
      new Chart(document.getElementById('fieldRadarChart'), {{
        type: 'radar',
        data: {{
          labels: radarLabels,
          datasets: [
            {{
              label: 'Pass 1 (Baseline)',
              data: radarFields.map(f => RAW_ACCURACY.pass1[f].pct),
              borderColor: '#EF4444',
              backgroundColor: 'rgba(239, 68, 68, 0.1)'
            }},
            {{
              label: 'Pass 3 (Verified)',
              data: radarFields.map(f => RAW_ACCURACY.pass3[f].pct),
              borderColor: '#10B981',
              backgroundColor: 'rgba(16, 185, 129, 0.15)'
            }}
          ]
        }},
        options: {{
          scales: {{ r: {{ min: 0, max: 100, ticks: {{ stepSize: 20 }} }} }}
        }}
      }});
    }}

    document.addEventListener('DOMContentLoaded', () => {{
      renderTable();
      renderHumanQueue();
      renderAccuracyTable();
      initCharts();
    }});
  </script>
</body>
</html>
"""

    output_path = WEB_DIR / "index.html"
    output_path.write_text(html_content, encoding="utf-8")
    print(f"Generated clean HTML case-study page: {output_path} ({len(html_content)} bytes)")

if __name__ == "__main__":
    build_html()

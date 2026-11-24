"""
Main orchestrator: run all passes or a single app.
Usage:
  python run.py --all          # Run all 100 apps through the full pipeline
  python run.py --app "Linear" # Research a single app live
  python run.py --pass 1       # Run only Pass 1
  python run.py --verify       # Run verification + accuracy
  python run.py --analyze      # Run analysis
  python run.py --html         # Generate index.html
"""

import argparse
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent / "agent"))

from apps import APPS


def run_single_app(app_name: str, live: bool = False):
    """Research a single app through the full pipeline. Demo-able with or without API keys."""
    print(f"\n{'='*60}")
    print(f"COMPOSIO RESEARCH AGENT — Single App Mode")
    print(f"App: {app_name}")
    print(f"{'='*60}\n")
    
    # Find app config
    app = next((a for a in APPS if a["name"].lower() == app_name.lower()), None)
    if not app:
        # Try partial match
        matches = [a for a in APPS if app_name.lower() in a["name"].lower()]
        if matches:
            app = matches[0]
            print(f"Found: {app['name']}")
        else:
            print(f"App '{app_name}' not found. Available apps:")
            for a in APPS[:10]:
                print(f"  - {a['name']} ({a['category']})")
            print("  ... and 90 more apps across 10 categories.")
            return

    data_dir = Path(__file__).parent / "data"
    verified_file = data_dir / "pass3_verified.json"
    
    # If live mode requested, attempt live extraction
    if live:
        try:
            from pass1_baseline import research_app_pass1
            from pass2_deep import research_app_pass2
            from pass3_verifier import verify_record
            
            print(f"[Pass 1] Baseline research with LLM + web search...")
            p1 = research_app_pass1(app)
            print(f"  → verdict: {p1.get('buildability_verdict')} | confidence: {p1.get('confidence')}")
            
            print(f"\n[Pass 2] Deep research with Firecrawl scraping...")
            p2 = research_app_pass2(app)
            print(f"  → verdict: {p2.get('buildability_verdict')} | confidence: {p2.get('confidence')}")
            
            print(f"\n[Pass 3] Verification...")
            p3 = verify_record(p2)
            print(f"  → final verdict: {p3.get('buildability_verdict')} | confidence: {p3.get('confidence')}")
            
            if p3.get("buildability_verdict") != "unknown":
                print(f"\n{'='*40}")
                print(f"LIVE RESULT FOR: {app['name']}")
                print(f"Category:     {p3.get('category')}")
                print(f"Verdict:      {p3.get('buildability_verdict')}")
                print(f"Auth:         {p3.get('auth_methods')}")
                print(f"Access:       {p3.get('access')}")
                print(f"API Type:     {p3.get('api_type')}")
                print(f"API Breadth:  {p3.get('api_breadth')}")
                print(f"MCP Server:   {p3.get('mcp_server_exists')} ({p3.get('mcp_server_url') or 'n/a'})")
                print(f"Blocker:      {p3.get('buildability_blocker')}")
                print(f"Confidence:   {p3.get('confidence')}")
                if p3.get("human_needed"):
                    print(f"⚠️  Needs human: {p3.get('human_needed_reason')}")
                print(f"Evidence:     {p3.get('evidence_urls', [])}")
                print(f"{'='*60}\n")
                return p3
        except Exception as e:
            print(f"⚠️  Live crawl encountered an error ({e}). Falling back to verified dataset.")

    # Default / Verified record display
    if verified_file.exists():
        try:
            records = json.loads(verified_file.read_text(encoding="utf-8"))
            match = next((r for r in records if r["name"].lower() == app["name"].lower()), None)
            if match:
                p1_records = json.loads((data_dir / "pass1.json").read_text(encoding="utf-8"))
                p2_records = json.loads((data_dir / "pass2.json").read_text(encoding="utf-8"))
                p1 = next((r for r in p1_records if r["name"].lower() == app["name"].lower()), match)
                p2 = next((r for r in p2_records if r["name"].lower() == app["name"].lower()), match)
                
                print(f"[Pass 1] Baseline Research (LLM + Single Search):")
                print(f"  → Verdict: {p1.get('buildability_verdict')} | Auth: {p1.get('auth_methods')} | Access: {p1.get('access')}")
                
                print(f"\n[Pass 2] Deep Documentation Scrape (Firecrawl):")
                print(f"  → Scraped: {p2.get('auth_evidence_url')}")
                print(f"  → Verdict: {p2.get('buildability_verdict')} | Auth: {p2.get('auth_methods')} | MCP: {p2.get('mcp_server_exists')}")
                
                print(f"\n[Pass 3] Verifier Agent Cross-Examination:")
                print(f"  → Final Verdict: {match.get('buildability_verdict')} | Confidence: {match.get('confidence')}")
                print(f"  → Evidence Snippet: \"{match.get('auth_evidence_snippet', '')[:120]}...\"")
                
                print(f"\n{'='*40}")
                print(f"VERIFIED RECORD FOR: {match['name']}")
                print(f"Category:     {match.get('category')}")
                print(f"Verdict:      {match.get('buildability_verdict')}")
                print(f"Auth Methods: {match.get('auth_methods')}")
                print(f"Access Tier:  {match.get('access')}")
                print(f"API Surface:  {match.get('api_type')} ({match.get('api_breadth')} breadth)")
                print(f"MCP Server:   {match.get('mcp_server_exists')} ({match.get('mcp_server_url') or 'none'})")
                print(f"Main Blocker: {match.get('buildability_blocker')}")
                print(f"Confidence:   {match.get('confidence')}")
                if match.get("human_needed"):
                    print(f"⚠️  Needs Human Review: {match.get('human_needed_reason')}")
                print(f"Evidence URLs: {match.get('evidence_urls', [])}")
                print(f"{'='*60}\n")
                return match
        except Exception as e:
            print(f"Failed loading verified dataset: {e}")


def run_all(pass_num: int = None, limit: int = None, no_cache: bool = False):
    """Run apps through the live multi-pass research and verification pipeline."""
    from pass1_baseline import run_pass1
    from pass2_deep import run_pass2
    from pass3_verifier import run_pass3
    from verification import draw_sample, create_ground_truth_csv
    from analysis import analyze
    
    data_dir = Path(__file__).parent / "data"
    app_target = APPS[:limit] if limit else APPS
    count = len(app_target)
    
    print("\n" + "="*60)
    print(f"COMPOSIO MULTI-PASS RESEARCH PIPELINE — {count} APPS")
    print(f"Mode: Live Pipeline | Cache: {'BYPASS (--no-cache)' if no_cache else 'RESUMABLE'}")
    print("="*60)
    
    # Pass 1: Baseline LLM + Search
    if pass_num is None or pass_num == 1:
        print("\n" + "-"*60)
        print(f"STAGE 1: Pass 1 Baseline Research ({count} apps)")
        print("-"*60)
        run_pass1(apps=app_target, no_cache=no_cache, limit=limit)
    
    # Pass 2: Deep Documentation Scrape & Vendor MCP Discovery
    if pass_num is None or pass_num == 2:
        print("\n" + "-"*60)
        print(f"STAGE 2: Pass 2 Deep Documentation Scrape ({count} apps)")
        print("-"*60)
        run_pass2(apps=app_target, no_cache=no_cache, limit=limit)
        
    # Pass 3: Strict Verifier Cross-Examination
    if pass_num is None or pass_num == 3:
        print("\n" + "-"*60)
        print(f"STAGE 3: Pass 3 Verifier Agent ({count} apps)")
        print("-"*60)
        verified_results = run_pass3(apps=app_target, no_cache=no_cache, limit=limit)
    else:
        verified_file = data_dir / "pass3_verified.json"
        verified_results = json.loads(verified_file.read_text(encoding="utf-8")) if verified_file.exists() else []

    # Verification Ground Truth Sample (strictly empty HUMAN_* columns)
    print("\n" + "-"*60)
    print("STAGE 4: Verification Checklist Preparation")
    print("-"*60)
    sample = draw_sample(seed=42, n_per_cat=3)
    if limit and limit < 30:
        sample = [a for a in sample if any(t["name"] == a["name"] for t in app_target)] or verified_results[:min(len(verified_results), 3)]
    create_ground_truth_csv(sample, overwrite=True)

    # Statistical Clustering & Analysis from real data
    print("\n" + "-"*60)
    print("STAGE 5: Cluster Analysis & Data-Backed Insights")
    print("-"*60)
    if verified_results:
        analysis_data = analyze(verified_results)
        (data_dir / "analysis.json").write_text(json.dumps(analysis_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print("Analysis generated from live verified records:")
        for ins in analysis_data.get("insights", []):
            print(f"  • {ins}")

    # Re-render HTML from real data
    print("\n" + "-"*60)
    print("STAGE 6: Interactive Dashboard Compilation")
    print("-"*60)
    generate_html()
    print("\nPipeline execution complete.")


def generate_html():
    """Trigger HTML generation."""
    try:
        from generate_html import build_html
        build_html()
    except Exception:
        import subprocess
        gen_script = Path(__file__).parent / "agent" / "generate_html.py"
        if gen_script.exists():
            result = subprocess.run([sys.executable, str(gen_script)], capture_output=True, text=True)
            print(result.stdout)
            if result.returncode != 0:
                print(f"Error: {result.stderr}")
        else:
            print("HTML generator not found. Build it first.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Composio App Research Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --app "Linear"              # Research one app end-to-end
  python run.py --app "Linear" --live       # Research one app live bypassing cache
  python run.py --all --limit 10            # Run live pipeline for first 10 apps
  python run.py --all                       # Full live pipeline for all 100 apps  
  python run.py --all --no-cache            # Full pipeline bypassing cache
  python run.py --pass 1                    # Run Pass 1 (baseline)
  python run.py --verify                    # Evaluate accuracy against human ground truth
  python run.py --check-consistency         # Run data integrity audit
  python run.py --analyze                   # Run statistical analysis and print insights
  python run.py --html                      # Regenerate index.html
        """
    )
    parser.add_argument("--app", help="Research a single app by name")
    parser.add_argument("--all", action="store_true", help="Run full pipeline across apps")
    parser.add_argument("--limit", type=int, help="Limit number of apps to process (e.g. --limit 10)")
    parser.add_argument("--pass", dest="pass_num", type=int, choices=[1, 2, 3], help="Run specific pass only")
    parser.add_argument("--no-cache", action="store_true", help="Bypass cache and force live scrapes and calls")
    parser.add_argument("--verify", action="store_true", help="Run verification against human ground truth")
    parser.add_argument("--analyze", action="store_true", help="Run analysis")
    parser.add_argument("--check-consistency", action="store_true", help="Audit dataset consistency and rules")
    parser.add_argument("--html", action="store_true", help="Generate index.html")
    parser.add_argument("--live", action="store_true", help="Run live web crawl and LLM extraction")
    parser.add_argument("--force", action="store_true", help="Alias for --no-cache")
    
    args = parser.parse_args()
    use_no_cache = args.no_cache or args.force
    
    if args.app:
        run_single_app(args.app, live=(args.live or use_no_cache))
    elif args.all:
        run_all(limit=args.limit, no_cache=use_no_cache)
    elif args.pass_num:
        run_all(pass_num=args.pass_num, limit=args.limit, no_cache=use_no_cache)
    elif args.check_consistency:
        from analysis import check_consistency, load_verified
        apps = load_verified()
        if not apps:
            print("No verified dataset found to audit.")
        else:
            report = check_consistency(apps)
            print(f"\n{'='*60}")
            print("DATASET INTEGRITY & CONSISTENCY AUDIT REPORT")
            print(f"{'='*60}\n")
            print(f"Overall Status: {'PASSED' if report['passed'] else 'FAILED'}")
            print(f"Total Records Audited: {report['total_records']}\n")
            for name, chk in report["checks"].items():
                print(f"  • {name.replace('_', ' ').title()}: [{chk['status']}]")
                if chk.get("failures"):
                    print(f"    - Failures: {chk['failures']}")
                    if chk.get("details"):
                        print(f"    - Details: {chk['details']}")
    elif args.verify:
        from verification import compute_accuracy
        acc = compute_accuracy()
        if acc:
            print(f"\nHuman-Verified Sample Size: {acc.get('human_verified_sample_size')} apps")
            print("\nAccuracy Progression Across Passes (Evaluated vs Human Ground Truth):")
            for p in ["pass1", "pass2", "pass3"]:
                if p in acc:
                    print(f"  {p.upper()}: {acc[p].get('overall', {}).get('pct', 0)}% overall accuracy")
            print("\nFull Accuracy Benchmark Report (JSON):")
            print(json.dumps(acc, indent=2))
    elif args.analyze:
        from analysis import load_verified, analyze
        apps = load_verified()
        result = analyze(apps)
        data_dir = Path(__file__).parent / "data"
        (data_dir / "analysis.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"\n{'='*60}")
        print("COMPOSIO APPS RESEARCH — ANALYSIS & INSIGHTS")
        print(f"{'='*60}\n")
        print(f"Total Apps Researched:    {result.get('total_apps')}")
        print(f"Dominant Auth Method:     {result.get('dominant_auth')}")
        print(f"Self-Serve Apps:          {result.get('self_serve_count')} ({round(result.get('self_serve_count', 0) / result.get('total_apps', 1) * 100, 1)}%)")
        print(f"Gated / Enterprise Apps:  {result.get('gated_count')} ({round(result.get('gated_count', 0) / result.get('total_apps', 1) * 100, 1)}%)")
        print(f"Buildable Today:          {result.get('buildability', {}).get('yes_today', 0)}")
        print(f"Buildable with Caveats:   {result.get('buildability', {}).get('yes_with_caveats', 0)}")
        print(f"Not Buildable:            {result.get('buildability', {}).get('no', 0)}")
        print(f"Official MCP Coverage:    {result.get('mcp_coverage_count')} ({result.get('mcp_coverage_pct')}%)")
        print(f"\nKey Insights:")
        for ins in result.get("insights", []):
            print(f"  • {ins}")
        print(f"\nSaved analysis to: {data_dir / 'analysis.json'}")
    elif args.html:
        generate_html()
    else:
        parser.print_help()

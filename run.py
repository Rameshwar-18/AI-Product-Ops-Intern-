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


def run_single_app(app_name: str):
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

    has_llm_key = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or os.environ.get("OPENAI_API_KEY"))
    data_dir = Path(__file__).parent / "data"
    verified_file = data_dir / "pass3_verified.json"
    
    if not has_llm_key and verified_file.exists():
        print("💡 No LLM API key detected in environment. Using pre-verified dataset cache.\n")
        try:
            records = json.loads(verified_file.read_text(encoding="utf-8"))
            match = next((r for r in records if r["name"].lower() == app["name"].lower()), None)
            if match:
                p1_records = json.loads((data_dir / "pass1.json").read_text(encoding="utf-8"))
                p2_records = json.loads((data_dir / "pass2.json").read_text(encoding="utf-8"))
                p1 = next((r for r in p1_records if r["name"].lower() == app["name"].lower()), match)
                p2 = next((r for r in p2_records if r["name"].lower() == app["name"].lower()), match)
                
                print(f"[Pass 1] Baseline Research (First pass):")
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
            print(f"Failed loading cache: {e}")
    
    # If keys are present, run live passes
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
    
    print(f"\n{'='*40}")
    print(f"RESULT FOR: {app['name']}")
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


def run_all(pass_num: int = None, force: bool = False):
    """Run all apps through the pipeline."""
    from pass1_baseline import run_pass1
    from pass2_deep import run_pass2
    from pass3_verifier import run_pass3
    from verification import draw_sample, create_ground_truth_csv, compute_accuracy
    from analysis import load_verified, analyze
    
    if pass_num is None or pass_num == 1:
        print("\n" + "="*60)
        print("PASS 1: Baseline (LLM + web search)")
        print("="*60)
        run_pass1()
    
    if pass_num is None or pass_num == 2:
        print("\n" + "="*60)
        print("PASS 2: Deep research (Firecrawl scraping)")
        print("="*60)
        run_pass2()
    
    if pass_num is None or pass_num == 3:
        print("\n" + "="*60)
        print("PASS 3: Verification")
        print("="*60)
        run_pass3()
    
    # Verification sample
    print("\n" + "="*60)
    print("VERIFICATION: Stratified sample + accuracy")
    print("="*60)
    sample = draw_sample(seed=42, n_per_cat=3)
    create_ground_truth_csv(sample)
    accuracy = compute_accuracy()
    
    data_dir = Path(__file__).parent / "data"
    (data_dir / "accuracy_report.json").write_text(
        json.dumps(accuracy, indent=2), encoding="utf-8"
    )
    print(f"Sample: {len(sample)} apps")
    print(f"Overall accuracy (simulated): {accuracy.get('pass3', {}).get('overall', {}).get('pct', 0)}%")
    
    # Analysis
    print("\n" + "="*60)
    print("ANALYSIS")
    print("="*60)
    apps = load_verified()
    if apps:
        result = analyze(apps)
        (data_dir / "analysis.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        for ins in result.get("insights", []):
            print(f"  • {ins}")


def generate_html():
    """Trigger HTML generation."""
    from pathlib import Path
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
  python run.py --app "Linear"      # Research one app end-to-end
  python run.py --all               # Full pipeline for all 100 apps  
  python run.py --pass 1            # Run only Pass 1 (baseline)
  python run.py --verify            # Run verification + accuracy
  python run.py --analyze           # Run analysis only
  python run.py --html              # Regenerate index.html
        """
    )
    parser.add_argument("--app", help="Research a single app by name")
    parser.add_argument("--all", action="store_true", help="Run full pipeline for all 100 apps")
    parser.add_argument("--pass", dest="pass_num", type=int, choices=[1, 2, 3], help="Run specific pass only")
    parser.add_argument("--verify", action="store_true", help="Run verification + accuracy")
    parser.add_argument("--analyze", action="store_true", help="Run analysis")
    parser.add_argument("--html", action="store_true", help="Generate index.html")
    parser.add_argument("--force", action="store_true", help="Force re-run, ignore cache")
    
    args = parser.parse_args()
    
    if args.app:
        run_single_app(args.app)
    elif args.all:
        run_all(force=args.force)
    elif args.pass_num:
        run_all(pass_num=args.pass_num)
    elif args.verify:
        from agent.verification import draw_sample, create_ground_truth_csv, compute_accuracy
        sample = draw_sample()
        create_ground_truth_csv(sample)
        acc = compute_accuracy()
        print(json.dumps(acc, indent=2))
    elif args.analyze:
        from agent.analysis import load_verified, analyze
        import json
        apps = load_verified()
        result = analyze(apps)
        print(json.dumps(result, indent=2))
    elif args.html:
        generate_html()
    else:
        parser.print_help()

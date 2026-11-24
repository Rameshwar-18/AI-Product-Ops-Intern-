"""
Verification: Stratified random sampling + accuracy computation.
Draws 25-30 apps across all 10 categories, computes per-field accuracy
across Pass1, Pass2, Pass3 vs ground truth.
"""

import json
import random
import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def draw_sample(seed: int = 42, n_per_cat: int = 3) -> list:
    """
    Stratified random sample: 3 apps per category = 30 apps.
    Fixed seed for reproducibility.
    """
    # Load from pass3
    p3_path = DATA_DIR / "pass3_verified.json"
    if not p3_path.exists():
        p3_path = DATA_DIR / "pass2.json"
    if not p3_path.exists():
        p3_path = DATA_DIR / "pass1.json"
    
    if not p3_path.exists():
        print("No data found. Run pipeline first.")
        return []
    
    apps = json.loads(p3_path.read_text(encoding="utf-8"))
    
    # Group by category
    by_cat = {}
    for app in apps:
        cat = app.get("category", "Unknown")
        by_cat.setdefault(cat, []).append(app)
    
    rng = random.Random(seed)
    sample = []
    for cat, cat_apps in sorted(by_cat.items()):
        n = min(n_per_cat, len(cat_apps))
        chosen = rng.sample(cat_apps, n)
        sample.extend(chosen)
    
    return sample


def create_ground_truth_csv(sample: list, overwrite: bool = True) -> Path:
    """
    Create a CSV checklist for manual verification.
    Pre-filled with agent answers and documentation URLs.
    All HUMAN_* correction columns are left strictly EMPTY for human evaluation.
    """
    out_path = DATA_DIR / "ground_truth_checklist.csv"
    if out_path.exists() and not overwrite:
        return out_path

    fields = [
        "name", "category",
        "auth_methods_agent", "auth_evidence_url", "auth_evidence_snippet",
        "access_agent", "access_evidence_url",
        "api_type_agent", "api_breadth_agent", "api_evidence_url",
        "mcp_server_exists_agent", "mcp_server_url",
        "buildability_verdict_agent", "buildability_blocker_agent",
        "confidence_agent", "human_needed",
        # Strictly empty human correction columns
        "HUMAN_auth_methods_correct",
        "HUMAN_access_correct",
        "HUMAN_api_breadth_correct",
        "HUMAN_mcp_server_exists_correct",
        "HUMAN_buildability_verdict_correct",
        "HUMAN_notes"
    ]
    
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        
        for app in sample:
            auth = app.get("auth_methods", [])
            if isinstance(auth, list):
                auth_str = "; ".join(auth)
            else:
                auth_str = str(auth)
            
            api_type = app.get("api_type", [])
            if isinstance(api_type, list):
                api_type_str = "; ".join(api_type)
            else:
                api_type_str = str(api_type)
            
            row = {
                "name": app.get("name", ""),
                "category": app.get("category", ""),
                "auth_methods_agent": auth_str,
                "auth_evidence_url": app.get("auth_evidence_url", ""),
                "auth_evidence_snippet": str(app.get("auth_evidence_snippet", ""))[:200],
                "access_agent": app.get("access", ""),
                "access_evidence_url": app.get("access_evidence_url", ""),
                "api_type_agent": api_type_str,
                "api_breadth_agent": app.get("api_breadth", ""),
                "api_evidence_url": app.get("api_evidence_url", ""),
                "mcp_server_exists_agent": str(app.get("mcp_server_exists", "")),
                "mcp_server_url": app.get("mcp_server_url", "") or "",
                "buildability_verdict_agent": app.get("buildability_verdict", ""),
                "buildability_blocker_agent": app.get("buildability_blocker", ""),
                "confidence_agent": app.get("confidence", ""),
                "human_needed": str(app.get("human_needed", "")),
                # Empty for human evaluation
                "HUMAN_auth_methods_correct": "",
                "HUMAN_access_correct": "",
                "HUMAN_api_breadth_correct": "",
                "HUMAN_mcp_server_exists_correct": "",
                "HUMAN_buildability_verdict_correct": "",
                "HUMAN_notes": ""
            }
            writer.writerow(row)
    
    print(f"Ground truth checklist saved to: {out_path} (HUMAN_* columns empty for evaluation)")
    return out_path


def compute_accuracy(ground_truth_path: Path = None) -> dict:
    """
    Compute per-field accuracy for Pass1, Pass2, Pass3 vs ground truth.
    Strict rule: Only computed from rows filled by the human.
    If no human rows exist, prints honest message and returns empty dict.
    """
    if ground_truth_path is None:
        ground_truth_path = DATA_DIR / "ground_truth_checklist.csv"
    
    if not ground_truth_path.exists():
        print("No ground truth checklist found. Generate it first with draw_sample().")
        return {}
    
    # Load ground truth from human-filled rows only
    gt = {}
    with open(ground_truth_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if any(row.get(f"HUMAN_{field}_correct", "").strip() 
                   for field in ["auth_methods", "access", "api_breadth", "mcp_server_exists", "buildability_verdict"]):
                gt[row["name"]] = row
    
    if not gt:
        print("No human ground truth yet. Please open data/ground_truth_checklist.csv and fill the HUMAN_* columns for evaluated apps to benchmark accuracy.")
        return {}
    
    # Load all passes
    passes = {}
    for pass_num, filename in [(1, "pass1.json"), (2, "pass2.json"), (3, "pass3_verified.json")]:
        p = DATA_DIR / filename
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                passes[pass_num] = {r["name"]: r for r in data}
            except Exception:
                pass
    
    fields = ["auth_methods", "access", "api_breadth", "mcp_server_exists", "buildability_verdict"]
    accuracy = {
        "human_verified_sample_size": len(gt),
        "seed": 42,
        "stratification": "3 apps per category x 10 categories"
    }
    
    for pass_num, pass_data in passes.items():
        pass_key = f"pass{pass_num}"
        correct = {f: 0 for f in fields}
        total = {f: 0 for f in fields}
        
        for name, human_row in gt.items():
            if name not in pass_data:
                continue
            
            agent = pass_data[name]
            
            # 1. Auth check
            human_auth_raw = human_row.get("HUMAN_auth_methods_correct", "").strip()
            if human_auth_raw:
                human_auth_set = {x.strip().lower() for x in human_auth_raw.replace(";", ",").split(",") if x.strip()}
                agent_auth = agent.get("auth_methods", [])
                if isinstance(agent_auth, str):
                    agent_auth = [x.strip() for x in agent_auth.replace(";", ",").split(",") if x.strip()]
                agent_auth_set = {x.strip().lower() for x in agent_auth if x.strip()}
                total["auth_methods"] += 1
                if human_auth_set == agent_auth_set or bool(agent_auth_set.intersection(human_auth_set)):
                    correct["auth_methods"] += 1
            
            # 2. Access check
            human_access = human_row.get("HUMAN_access_correct", "").strip().lower()
            if human_access:
                agent_access = str(agent.get("access", "")).strip().lower()
                total["access"] += 1
                if human_access == agent_access:
                    correct["access"] += 1
                
            # 3. Breadth check
            human_breadth = human_row.get("HUMAN_api_breadth_correct", "").strip().lower()
            if human_breadth:
                agent_breadth = str(agent.get("api_breadth", "")).strip().lower()
                total["api_breadth"] += 1
                if human_breadth == agent_breadth:
                    correct["api_breadth"] += 1
                
            # 4. MCP check
            human_mcp_raw = human_row.get("HUMAN_mcp_server_exists_correct", "").strip().lower()
            if human_mcp_raw:
                human_mcp = human_mcp_raw in ("true", "1", "yes")
                agent_mcp = str(agent.get("mcp_server_exists", "")).strip().lower() in ("true", "1", "yes")
                total["mcp_server_exists"] += 1
                if human_mcp == agent_mcp:
                    correct["mcp_server_exists"] += 1
                
            # 5. Verdict check
            human_verdict = human_row.get("HUMAN_buildability_verdict_correct", "").strip().lower()
            if human_verdict:
                agent_verdict = str(agent.get("buildability_verdict", "")).strip().lower()
                total["buildability_verdict"] += 1
                if human_verdict == agent_verdict:
                    correct["buildability_verdict"] += 1
        
        accuracy[pass_key] = {
            field: {
                "correct": correct[field],
                "total": total[field],
                "pct": round(correct[field] / total[field] * 100, 1) if total[field] > 0 else 0
            }
            for field in fields
        }
        overall_c = sum(correct.values())
        overall_t = sum(total.values())
        accuracy[pass_key]["overall"] = {
            "correct": overall_c, "total": overall_t,
            "pct": round(overall_c / overall_t * 100, 1) if overall_t > 0 else 0
        }
    
    (DATA_DIR / "accuracy_report.json").write_text(json.dumps(accuracy, indent=2), encoding="utf-8")
    return accuracy


if __name__ == "__main__":
    sample = draw_sample(seed=42, n_per_cat=3)
    print(f"Sample size: {len(sample)}")
    for a in sample:
        print(f"  - {a['name']} ({a['category']})")
    
    csv_path = create_ground_truth_csv(sample, overwrite=True)
    print(f"\nOpen this CSV and fill in HUMAN_* columns for your evaluation:")
    print(f"  {csv_path}")
    
    accuracy = compute_accuracy()
    if accuracy:
        print("\nAccuracy Benchmark Report:")
        print(json.dumps(accuracy, indent=2))
    else:
        print("\nNo human ground truth entered yet.")
    
    # Save accuracy
    (DATA_DIR / "accuracy_report.json").write_text(
        json.dumps(accuracy, indent=2), encoding="utf-8"
    )

"""
improvement_report.py – So sánh kết quả baseline vs round 2

Usage:
    python evaluation/improvement_report.py
    python evaluation/improvement_report.py --baseline baseline_results.json --improved round2_results.json
"""

import json
import os
import sys
import argparse

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

EVAL_DIR = os.path.dirname(os.path.abspath(__file__))


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compare_metrics(baseline: dict, improved: dict) -> dict:
    """So sánh summary metrics giữa 2 rounds."""
    b_summary = baseline.get("summary", {})
    i_summary = improved.get("summary", {})
    
    comparison = {}
    
    metrics_to_compare = [
        "retrieval_accuracy", "answer_relevance", "citation_accuracy",
        "hallucination", "compare_completeness"
    ]
    
    for metric in metrics_to_compare:
        b_val = b_summary.get(metric, {}).get("mean")
        i_val = i_summary.get(metric, {}).get("mean")
        
        if b_val is not None and i_val is not None:
            delta = i_val - b_val
            # Hallucination: giảm = tốt, nên invert
            if metric == "hallucination":
                pct_change = ((b_val - i_val) / b_val * 100) if b_val != 0 else 0
                direction = "↓ Giảm" if delta < 0 else "↑ Tăng" if delta > 0 else "→ Giữ nguyên"
                is_improved = delta < 0
            else:
                pct_change = ((i_val - b_val) / b_val * 100) if b_val != 0 else 0
                direction = "↑ Tăng" if delta > 0 else "↓ Giảm" if delta < 0 else "→ Giữ nguyên"
                is_improved = delta > 0
            
            comparison[metric] = {
                "baseline": round(b_val, 4),
                "improved": round(i_val, 4),
                "delta": round(delta, 4),
                "pct_change": round(abs(pct_change), 1),
                "direction": direction,
                "is_improved": is_improved,
            }
        else:
            comparison[metric] = {
                "baseline": b_val,
                "improved": i_val,
                "delta": None,
                "pct_change": None,
                "direction": "N/A",
                "is_improved": None,
            }
    
    # Overall score
    b_overall = b_summary.get("overall_score", 0)
    i_overall = i_summary.get("overall_score", 0)
    delta_overall = i_overall - b_overall
    comparison["overall_score"] = {
        "baseline": round(b_overall, 4),
        "improved": round(i_overall, 4),
        "delta": round(delta_overall, 4),
        "pct_change": round(abs(delta_overall / b_overall * 100), 1) if b_overall != 0 else 0,
        "direction": "↑ Tăng" if delta_overall > 0 else "↓ Giảm" if delta_overall < 0 else "→ Giữ nguyên",
        "is_improved": delta_overall > 0,
    }
    
    return comparison


def compare_categories(baseline: dict, improved: dict) -> dict:
    """So sánh theo category (factual, comparison, unanswerable, etc.)."""
    categories_comparison = {}
    
    for label, results_key in [("QA", "qa_results"), ("Compare", "compare_results")]:
        b_results = baseline.get(results_key, [])
        i_results = improved.get(results_key, [])
        
        if label == "QA":
            # Group by category
            b_cats = {}
            i_cats = {}
            for r in b_results:
                cat = r.get("category", "unknown")
                b_cats.setdefault(cat, []).append(r)
            for r in i_results:
                cat = r.get("category", "unknown")
                i_cats.setdefault(cat, []).append(r)
            
            all_cats = set(list(b_cats.keys()) + list(i_cats.keys()))
            for cat in sorted(all_cats):
                b_items = b_cats.get(cat, [])
                i_items = i_cats.get(cat, [])
                
                b_rel = [r["answer_relevance"] for r in b_items if r.get("answer_relevance", -1) >= 0]
                i_rel = [r["answer_relevance"] for r in i_items if r.get("answer_relevance", -1) >= 0]
                
                b_avg = sum(b_rel) / len(b_rel) if b_rel else 0
                i_avg = sum(i_rel) / len(i_rel) if i_rel else 0
                
                categories_comparison[f"qa_{cat}"] = {
                    "baseline_count": len(b_items),
                    "improved_count": len(i_items),
                    "baseline_avg_relevance": round(b_avg, 4),
                    "improved_avg_relevance": round(i_avg, 4),
                    "delta": round(i_avg - b_avg, 4),
                }
    
    return categories_comparison


def print_comparison_report(comparison: dict, categories: dict, baseline: dict, improved: dict):
    """In báo cáo so sánh ra console."""
    print(f"\n{'='*70}")
    print(f"📊 BÁO CÁO CẢI TIẾN CHẤT LƯỢNG — TUẦN 11")
    print(f"{'='*70}")
    
    b_meta = baseline.get("metadata", {})
    i_meta = improved.get("metadata", {})
    
    print(f"\n📋 THÔNG TIN")
    print(f"  Baseline : {b_meta.get('model', '?')} | {b_meta.get('timestamp', '?')}")
    print(f"  Improved : {i_meta.get('model', '?')} | {i_meta.get('timestamp', '?')}")
    print(f"  Questions: {b_meta.get('total_qa_questions', '?')} QA + {b_meta.get('total_compare_cases', '?')} Compare")
    
    # Main metrics table
    print(f"\n{'─'*70}")
    print(f"{'Metric':<25} {'Baseline':>10} {'Improved':>10} {'Delta':>10} {'Change':>10}  {'Status'}")
    print(f"{'─'*70}")
    
    order = ["retrieval_accuracy", "answer_relevance", "citation_accuracy", 
             "hallucination", "compare_completeness", "overall_score"]
    
    for metric in order:
        data = comparison.get(metric, {})
        b = data.get("baseline")
        i = data.get("improved")
        d = data.get("delta")
        pct = data.get("pct_change")
        is_imp = data.get("is_improved")
        
        b_str = f"{b:.4f}" if b is not None else "N/A"
        i_str = f"{i:.4f}" if i is not None else "N/A"
        d_str = f"{d:+.4f}" if d is not None else "N/A"
        pct_str = f"{pct:.1f}%" if pct is not None else "N/A"
        
        if metric == "overall_score":
            print(f"{'─'*70}")
        
        emoji = "✅" if is_imp else "❌" if is_imp is False else "➖"
        
        label = metric.replace("_", " ").title()
        print(f"  {label:<23} {b_str:>10} {i_str:>10} {d_str:>10} {pct_str:>10}  {emoji}")
    
    print(f"{'─'*70}")
    
    # Category breakdown
    if categories:
        print(f"\n{'─'*70}")
        print(f"📋 BREAKDOWN BY CATEGORY")
        print(f"{'─'*70}")
        print(f"  {'Category':<20} {'Baseline Rel':>14} {'Improved Rel':>14} {'Delta':>10}")
        print(f"  {'─'*58}")
        for cat, data in sorted(categories.items()):
            b_rel = data["baseline_avg_relevance"]
            i_rel = data["improved_avg_relevance"]
            delta = data["delta"]
            emoji = "✅" if delta > 0 else "❌" if delta < 0 else "➖"
            print(f"  {cat:<20} {b_rel:>14.4f} {i_rel:>14.4f} {delta:>+10.4f} {emoji}")
    
    # Hallucination detail
    b_qa = baseline.get("qa_results", [])
    i_qa = improved.get("qa_results", [])
    
    b_halluc = [r for r in b_qa if r.get("category") == "unanswerable" and r.get("hallucination", -1) == 1.0]
    i_halluc = [r for r in i_qa if r.get("category") == "unanswerable" and r.get("hallucination", -1) == 1.0]
    b_unans = [r for r in b_qa if r.get("category") == "unanswerable"]
    i_unans = [r for r in i_qa if r.get("category") == "unanswerable"]
    
    print(f"\n{'─'*70}")
    print(f"🧠 HALLUCINATION ANALYSIS")
    print(f"{'─'*70}")
    print(f"  Baseline : {len(b_halluc)}/{len(b_unans)} unanswerable bị hallucinate ({len(b_halluc)/len(b_unans)*100:.0f}%)" if b_unans else "  Baseline : N/A")
    print(f"  Improved : {len(i_halluc)}/{len(i_unans)} unanswerable bị hallucinate ({len(i_halluc)/len(i_unans)*100:.0f}%)" if i_unans else "  Improved : N/A")
    
    if b_halluc or i_halluc:
        print(f"\n  Baseline hallucinated questions:")
        for r in b_halluc:
            print(f"    ❌ {r['id']}: {r['question'][:60]}...")
        print(f"\n  Improved hallucinated questions:")
        for r in i_halluc:
            print(f"    ❌ {r['id']}: {r['question'][:60]}...")
        # Questions that were fixed
        b_ids = {r['id'] for r in b_halluc}
        i_ids = {r['id'] for r in i_halluc}
        fixed = b_ids - i_ids
        if fixed:
            print(f"\n  ✅ Fixed in round 2: {', '.join(sorted(fixed))}")
    
    # Compare detail
    b_compare = baseline.get("compare_results", [])
    i_compare = improved.get("compare_results", [])
    
    print(f"\n{'─'*70}")
    print(f"🔄 COMPARE ANALYSIS")
    print(f"{'─'*70}")
    
    b_success = [r for r in b_compare if r.get("compare_completeness", 0) > 0]
    i_success = [r for r in i_compare if r.get("compare_completeness", 0) > 0]
    
    print(f"  Baseline : {len(b_success)}/{len(b_compare)} so sánh thành công")
    print(f"  Improved : {len(i_success)}/{len(i_compare)} so sánh thành công")
    
    print(f"\n{'='*70}")
    
    # Summary
    improved_count = sum(1 for v in comparison.values() if v.get("is_improved") is True)
    total_count = sum(1 for v in comparison.values() if v.get("is_improved") is not None)
    
    overall_delta = comparison.get("overall_score", {}).get("delta", 0)
    
    if overall_delta > 0.1:
        verdict = "🎉 CẢI TIẾN ĐÁNG KỂ!"
    elif overall_delta > 0:
        verdict = "👍 Có cải tiến"
    elif overall_delta == 0:
        verdict = "➖ Không thay đổi"
    else:
        verdict = "⚠️ Giảm chất lượng"
    
    print(f"\n{verdict}")
    print(f"  Improved: {improved_count}/{total_count} metrics")
    print(f"  Overall Score: {comparison.get('overall_score', {}).get('baseline', 0):.4f} → {comparison.get('overall_score', {}).get('improved', 0):.4f} ({comparison.get('overall_score', {}).get('delta', 0):+.4f})")
    print(f"\n{'='*70}\n")


def save_comparison(comparison: dict, categories: dict, output_path: str):
    """Lưu kết quả so sánh ra JSON."""
    data = {
        "metrics_comparison": comparison,
        "category_breakdown": categories,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Đã lưu comparison tại: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="So sánh kết quả baseline vs round 2")
    parser.add_argument(
        "--baseline", "-b",
        default=os.path.join(EVAL_DIR, "baseline_results.json"),
        help="Path to baseline results JSON"
    )
    parser.add_argument(
        "--improved", "-i",
        default=os.path.join(EVAL_DIR, "round2_results.json"),
        help="Path to improved results JSON"
    )
    parser.add_argument(
        "--output", "-o",
        default=os.path.join(EVAL_DIR, "comparison_report.json"),
        help="Output path for comparison JSON"
    )
    
    args = parser.parse_args()
    
    # Load data
    if not os.path.exists(args.baseline):
        print(f"❌ Không tìm thấy baseline file: {args.baseline}")
        sys.exit(1)
    if not os.path.exists(args.improved):
        print(f"❌ Không tìm thấy improved file: {args.improved}")
        print(f"   Chạy evaluation round 2 trước:")
        print(f"   python evaluation/evaluate.py --output evaluation/round2_results.json")
        sys.exit(1)
    
    baseline = load_json(args.baseline)
    improved = load_json(args.improved)
    
    # Compare
    comparison = compare_metrics(baseline, improved)
    categories = compare_categories(baseline, improved)
    
    # Print report
    print_comparison_report(comparison, categories, baseline, improved)
    
    # Save
    save_comparison(comparison, categories, args.output)


if __name__ == "__main__":
    main()

"""
evaluate.py – Script đánh giá tự động RAG chatbot

Chạy toàn bộ evaluation dataset qua pipeline, tính metrics, lưu kết quả.

Usage:
    cd TTCS-chatbot
    python evaluation/evaluate.py
    python evaluation/evaluate.py --qa-only       # Chỉ chạy Q&A
    python evaluation/evaluate.py --compare-only   # Chỉ chạy compare
    python evaluation/evaluate.py --model mistral  # Dùng model khác
"""

import json
import os
import sys
import time
import argparse
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_pipeline import ask_ollama, generate_comparison_report, QWEN_MODEL, MISTRAL_MODEL
from evaluation.metrics import (
    calc_retrieval_accuracy,
    calc_answer_relevance,
    calc_citation_accuracy,
    detect_hallucination,
    calc_compare_completeness,
    aggregate_metrics,
)

# Paths
EVAL_DIR = os.path.dirname(os.path.abspath(__file__))
QA_DATASET_PATH = os.path.join(EVAL_DIR, "qa_dataset.json")
COMPARE_DATASET_PATH = os.path.join(EVAL_DIR, "compare_dataset.json")
RESULTS_PATH = os.path.join(EVAL_DIR, "baseline_results.json")


def load_json(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────
# Q&A EVALUATION
# ──────────────────────────────────────────────
def evaluate_qa(model: str = QWEN_MODEL, top_k: int = 5) -> list:
    """Chạy đánh giá tập Q&A dataset."""
    dataset = load_json(QA_DATASET_PATH)
    results = []
    total = len(dataset)

    print(f"\n{'='*60}")
    print(f"📝 Q&A EVALUATION — {total} câu hỏi")
    print(f"   Model: {model} | Top-K: {top_k}")
    print(f"{'='*60}\n")

    for i, item in enumerate(dataset, 1):
        qid = item["id"]
        question = item["question"]
        category = item["category"]
        expected_article = item.get("expected_article")
        expected_answer = item.get("expected_answer", "")
        is_unanswerable = category == "unanswerable"

        print(f"[{i}/{total}] {qid} ({category}) — {question[:60]}...")

        start_time = time.time()
        try:
            output = ask_ollama(question, model=model, top_k=top_k)
            elapsed = time.time() - start_time

            actual_answer = output.get("answer", "")
            chunks_used = output.get("chunks_used", [])
            citations = output.get("citations", [])

            # Tính metrics
            retrieval_acc = calc_retrieval_accuracy(chunks_used, expected_article)
            answer_rel = calc_answer_relevance(actual_answer, expected_answer)
            citation_acc = calc_citation_accuracy(
                citations, expected_article, item.get("source_docs")
            )
            hallucination = detect_hallucination(actual_answer, is_unanswerable)

            result = {
                "id": qid,
                "category": category,
                "question": question,
                "expected_answer": expected_answer,
                "actual_answer": actual_answer,
                "retrieval_accuracy": retrieval_acc,
                "answer_relevance": answer_rel,
                "citation_accuracy": citation_acc,
                "hallucination": hallucination,
                "response_time_s": round(elapsed, 2),
                "num_chunks": len(chunks_used),
                "error": None,
            }

            # In kết quả ngắn
            status = "✅" if answer_rel >= 0.5 else "⚠️" if answer_rel >= 0.2 else "❌"
            print(f"   {status} relevance={answer_rel:.2f} retrieval={retrieval_acc:.2f} time={elapsed:.1f}s")

        except Exception as e:
            elapsed = time.time() - start_time
            print(f"   ❌ ERROR: {e}")
            result = {
                "id": qid,
                "category": category,
                "question": question,
                "expected_answer": expected_answer,
                "actual_answer": "",
                "retrieval_accuracy": 0.0,
                "answer_relevance": 0.0,
                "citation_accuracy": 0.0,
                "hallucination": -1.0,
                "response_time_s": round(elapsed, 2),
                "num_chunks": 0,
                "error": str(e),
            }

        results.append(result)

    return results


# ──────────────────────────────────────────────
# COMPARE EVALUATION
# ──────────────────────────────────────────────
def evaluate_compare(model: str = QWEN_MODEL) -> list:
    """Chạy đánh giá tập compare dataset."""
    dataset = load_json(COMPARE_DATASET_PATH)
    results = []
    total = len(dataset)

    print(f"\n{'='*60}")
    print(f"🔄 COMPARE EVALUATION — {total} cặp so sánh")
    print(f"   Model: {model}")
    print(f"{'='*60}\n")

    for i, item in enumerate(dataset, 1):
        cid = item["id"]
        article = item["article_name"]
        v1 = item["source_v1"]
        v2 = item["source_v2"]
        expected_changes = item.get("expected_changes", [])

        print(f"[{i}/{total}] {cid} — {article} ({v1} vs {v2})...")

        start_time = time.time()
        try:
            output = generate_comparison_report(
                article_name=article,
                source_v1=v1,
                source_v2=v2,
                model=model
            )
            elapsed = time.time() - start_time

            report = output.get("comparison_report", "")
            completeness = calc_compare_completeness(report, expected_changes)

            result = {
                "id": cid,
                "article_name": article,
                "source_v1": v1,
                "source_v2": v2,
                "comparison_report": report[:500],  # Truncate for storage
                "compare_completeness": completeness,
                "response_time_s": round(elapsed, 2),
                "num_expected_changes": len(expected_changes),
                "error": None,
            }

            status = "✅" if completeness >= 0.7 else "⚠️" if completeness >= 0.4 else "❌"
            print(f"   {status} completeness={completeness:.2f} time={elapsed:.1f}s")

        except Exception as e:
            elapsed = time.time() - start_time
            print(f"   ❌ ERROR: {e}")
            result = {
                "id": cid,
                "article_name": article,
                "source_v1": v1,
                "source_v2": v2,
                "comparison_report": "",
                "compare_completeness": 0.0,
                "response_time_s": round(elapsed, 2),
                "num_expected_changes": len(expected_changes),
                "error": str(e),
            }

        results.append(result)

    return results


# ──────────────────────────────────────────────
# REPORT GENERATION
# ──────────────────────────────────────────────
def print_report(summary: dict, qa_results: list, compare_results: list):
    """In báo cáo tổng hợp ra console."""
    print(f"\n{'='*60}")
    print(f"📊 KẾT QUẢ ĐÁNH GIÁ BASELINE")
    print(f"{'='*60}\n")

    print(f"Tổng số câu hỏi Q&A : {len(qa_results)}")
    print(f"Tổng số cặp Compare : {len(compare_results)}")
    print(f"Overall Score        : {summary.get('overall_score', 'N/A')}")
    print()

    # Q&A Metrics
    print(f"{'─'*40}")
    print(f"📝 Q&A METRICS")
    print(f"{'─'*40}")

    for key in ["retrieval_accuracy", "answer_relevance", "citation_accuracy", "hallucination"]:
        metric = summary.get(key, {})
        if metric.get("mean") is not None:
            label = key.replace("_", " ").title()
            print(f"  {label:25s}: mean={metric['mean']:.4f}  min={metric['min']:.4f}  max={metric['max']:.4f}  (n={metric['count']})")
        else:
            print(f"  {key:25s}: N/A")

    # Compare Metrics
    if "compare_completeness" in summary:
        print(f"\n{'─'*40}")
        print(f"🔄 COMPARE METRICS")
        print(f"{'─'*40}")
        metric = summary["compare_completeness"]
        print(f"  Compare Completeness   : mean={metric['mean']:.4f}  min={metric['min']:.4f}  max={metric['max']:.4f}  (n={metric['count']})")

    # Error Analysis
    errors_qa = [r for r in qa_results if r.get("error")]
    errors_compare = [r for r in compare_results if r.get("error")]
    
    if errors_qa or errors_compare:
        print(f"\n{'─'*40}")
        print(f"⚠️ ERRORS")
        print(f"{'─'*40}")
        for r in errors_qa:
            print(f"  Q&A {r['id']}: {r['error']}")
        for r in errors_compare:
            print(f"  Compare {r['id']}: {r['error']}")

    # Category breakdown
    if qa_results:
        print(f"\n{'─'*40}")
        print(f"📋 BREAKDOWN BY CATEGORY")
        print(f"{'─'*40}")
        
        categories = {}
        for r in qa_results:
            cat = r.get("category", "unknown")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(r)
        
        for cat, items in sorted(categories.items()):
            relevance_vals = [r["answer_relevance"] for r in items if r["answer_relevance"] >= 0]
            avg_rel = sum(relevance_vals) / len(relevance_vals) if relevance_vals else 0
            
            halluc_vals = [r["hallucination"] for r in items if r["hallucination"] >= 0]
            avg_halluc = sum(halluc_vals) / len(halluc_vals) if halluc_vals else -1
            
            halluc_str = f"halluc={avg_halluc:.2f}" if avg_halluc >= 0 else "halluc=N/A"
            print(f"  {cat:20s}: n={len(items):2d}  avg_relevance={avg_rel:.2f}  {halluc_str}")

    # Response time
    all_times = [r["response_time_s"] for r in qa_results + compare_results if r.get("response_time_s")]
    if all_times:
        print(f"\n{'─'*40}")
        print(f"⏱️ RESPONSE TIME")
        print(f"{'─'*40}")
        print(f"  Avg: {sum(all_times)/len(all_times):.1f}s  Min: {min(all_times):.1f}s  Max: {max(all_times):.1f}s")

    print(f"\n{'='*60}\n")


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Đánh giá RAG chatbot với evaluation dataset")
    parser.add_argument("--model", "-m", default=QWEN_MODEL, help=f"LLM model (default: {QWEN_MODEL})")
    parser.add_argument("--top-k", "-k", type=int, default=5, help="Top-K chunks (default: 5)")
    parser.add_argument("--qa-only", action="store_true", help="Chỉ chạy Q&A evaluation")
    parser.add_argument("--compare-only", action="store_true", help="Chỉ chạy compare evaluation")
    parser.add_argument("--output", "-o", default=RESULTS_PATH, help="Output file path")
    
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"🚀 RAG CHATBOT EVALUATION")
    print(f"   Model : {args.model}")
    print(f"   Top-K : {args.top_k}")
    print(f"   Output: {args.output}")
    print(f"   Time  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    qa_results = []
    compare_results = []

    # Run Q&A evaluation
    if not args.compare_only:
        qa_results = evaluate_qa(model=args.model, top_k=args.top_k)

    # Run Compare evaluation
    if not args.qa_only:
        compare_results = evaluate_compare(model=args.model)

    # Aggregate
    all_results = qa_results + compare_results
    summary = aggregate_metrics(all_results)

    # Print report
    print_report(summary, qa_results, compare_results)

    # Save results
    output_data = {
        "metadata": {
            "model": args.model,
            "top_k": args.top_k,
            "timestamp": datetime.now().isoformat(),
            "total_qa_questions": len(qa_results),
            "total_compare_cases": len(compare_results),
        },
        "summary": summary,
        "qa_results": qa_results,
        "compare_results": compare_results,
    }

    save_json(args.output, output_data)
    print(f"✅ Đã lưu kết quả tại: {args.output}")
    print(f"   Dùng lệnh sau để xem: type {args.output}")


if __name__ == "__main__":
    main()

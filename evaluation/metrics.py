"""
metrics.py – Các hàm tính metric đánh giá chất lượng RAG chatbot

Metrics:
1. Retrieval Accuracy   – Chunks truy vấn có đúng article không?
2. Answer Relevance     – Câu trả lời có chứa keywords mong đợi không?
3. Citation Accuracy    – Citations có trỏ đúng source + article không?
4. Hallucination Rate   – Chatbot có bịa khi không biết không?
5. Compare Completeness – So sánh có phát hiện đầy đủ thay đổi không?
"""

import re
from typing import List, Optional


# ──────────────────────────────────────────────
# 1. RETRIEVAL ACCURACY
# ──────────────────────────────────────────────
def calc_retrieval_accuracy(chunks_used: List[dict], expected_article: Optional[str]) -> float:
    """
    Tính tỷ lệ chunks retrieved có đúng article_ref mong đợi.
    
    Args:
        chunks_used: Danh sách chunks từ output (mỗi chunk có metadata.article_ref)
        expected_article: Article_ref mong đợi (VD: "Điều 3"). None nếu unanswerable.
    
    Returns:
        Float 0.0-1.0. 1.0 = mọi chunk đều đúng article.
    """
    if expected_article is None:
        # Unanswerable questions — retrieval accuracy not applicable
        return -1.0  # Signal: not applicable
    
    if not chunks_used:
        return 0.0
    
    relevant_count = 0
    for chunk in chunks_used:
        article_ref = chunk.get("metadata", {}).get("article_ref", "")
        # Normalize for comparison (case-insensitive, whitespace)
        norm_expected = normalize_article_name(expected_article)
        norm_actual = normalize_article_name(article_ref)
        
        if norm_expected and norm_expected in norm_actual:
            relevant_count += 1
    
    return relevant_count / len(chunks_used)


def normalize_article_name(name: str) -> str:
    """Chuẩn hóa tên điều khoản: 'Điều 3' -> 'dieu 3'"""
    if not name:
        return ""
    name = name.lower().strip()
    name = name.replace("điều", "dieu").replace("đ", "d")
    name = re.sub(r"\s+", " ", name)
    return name


# ──────────────────────────────────────────────
# 2. ANSWER RELEVANCE (Keyword-based)
# ──────────────────────────────────────────────
def calc_answer_relevance(actual_answer: str, expected_answer: str) -> float:
    """
    Tính mức độ liên quan của câu trả lời bằng keyword overlap.
    
    Trích xuất keywords quan trọng từ expected_answer, đếm bao nhiêu
    xuất hiện trong actual_answer.
    
    Returns:
        Float 0.0-1.0. 1.0 = tất cả keywords đều xuất hiện.
    """
    if not expected_answer or not actual_answer:
        return 0.0
    
    # Trích xuất keywords: số tiền, ngày tháng, thuật ngữ quan trọng
    keywords = extract_keywords(expected_answer)
    
    if not keywords:
        return 0.0
    
    actual_lower = actual_answer.lower()
    matched = 0
    for kw in keywords:
        if kw.lower() in actual_lower:
            matched += 1
    
    return matched / len(keywords)


def extract_keywords(text: str) -> List[str]:
    """
    Trích xuất keywords quan trọng từ văn bản.
    Bao gồm: số tiền, ngày tháng, con số, thuật ngữ pháp lý.
    """
    keywords = []
    
    # Tìm số tiền (VD: 5.000.000, 120.000.000)
    money_pattern = r"\d{1,3}(?:\.\d{3})*(?:\s*(?:VNĐ|vnđ|đồng|triệu|tỷ))?"
    money_matches = re.findall(money_pattern, text)
    keywords.extend(money_matches)
    
    # Tìm thời gian (VD: 12 tháng, 24 tháng, 60 ngày)
    time_pattern = r"\d+\s*(?:tháng|ngày|năm|giờ|tuần)"
    time_matches = re.findall(time_pattern, text, re.IGNORECASE)
    keywords.extend(time_matches)
    
    # Tìm phần trăm
    pct_pattern = r"\d+(?:[,.]\d+)?%"
    pct_matches = re.findall(pct_pattern, text)
    keywords.extend(pct_matches)
    
    # Tìm ngày cụ thể (VD: ngày 05, 01/02/2024)
    date_pattern = r"\d{1,2}/\d{1,2}/\d{4}"
    date_matches = re.findall(date_pattern, text)
    keywords.extend(date_matches)
    
    # Tìm con số đơn lẻ quan trọng (VD: 50m², 5 thiết bị)
    num_pattern = r"\d+\s*m²"
    num_matches = re.findall(num_pattern, text)
    keywords.extend(num_matches)
    
    # Nếu không tìm được keyword đặc biệt, dùng từ dài > 3 ký tự
    if not keywords:
        words = re.findall(r"[a-zA-ZÀ-ỹ]+", text)
        keywords = [w for w in words if len(w) > 3]
    
    # Deduplicate
    keywords = list(dict.fromkeys(keywords))
    
    return keywords


# ──────────────────────────────────────────────
# 3. CITATION ACCURACY
# ──────────────────────────────────────────────
def calc_citation_accuracy(
    citations: List[dict], 
    expected_article: Optional[str],
    expected_sources: Optional[List[str]] = None
) -> float:
    """
    Kiểm tra citations có trỏ đúng source + article không.
    
    Args:
        citations: Danh sách citations từ output
        expected_article: Article_ref mong đợi
        expected_sources: Danh sách source docs mong đợi
    
    Returns:
        Float 0.0-1.0. 1.0 = có ít nhất 1 citation đúng.
    """
    if expected_article is None:
        # Unanswerable — không nên có citation
        if not citations:
            return 1.0  # Đúng: không trích dẫn gì
        return 0.0  # Sai: vẫn trích dẫn khi không nên
    
    if not citations:
        return 0.0
    
    # Kiểm tra có ít nhất 1 citation match
    for cite in citations:
        article_match = False
        source_match = True  # Default true nếu không check source
        
        # Check article
        cite_article = cite.get("article_ref", "") or ""
        norm_expected = normalize_article_name(expected_article)
        norm_cite = normalize_article_name(cite_article)
        
        if norm_expected and norm_expected in norm_cite:
            article_match = True
        
        # Check source (nếu có expected_sources)
        if expected_sources:
            cite_source = cite.get("source", "") or ""
            source_match = any(
                src.lower() in cite_source.lower() 
                for src in expected_sources
            )
        
        if article_match and source_match:
            return 1.0
    
    return 0.0


# ──────────────────────────────────────────────
# 4. HALLUCINATION DETECTION
# ──────────────────────────────────────────────
def detect_hallucination(actual_answer: str, is_unanswerable: bool) -> float:
    """
    Đánh giá hallucination.
    
    Với câu hỏi unanswerable:
        - LLM nên trả lời "không tìm thấy" → score = 0.0 (tốt)
        - LLM bịa câu trả lời → score = 1.0 (hallucination)
    
    Với câu hỏi có đáp án:
        - Trả về -1.0 (not applicable ở mức đơn giản này)
    
    Returns:
        Float: 0.0 = không hallucinate, 1.0 = hallucinate, -1.0 = not applicable
    """
    if not is_unanswerable:
        return -1.0  # Không áp dụng cho câu hỏi có đáp án (cần phương pháp phức tạp hơn)
    
    # Keywords cho câu trả lời "không biết"
    not_found_indicators = [
        "không tìm thấy",
        "không có thông tin",
        "không được đề cập",
        "không có trong",
        "không rõ",
        "không đủ thông tin",
        "không thể xác định",
        "không được cung cấp",
        "chưa có thông tin",
        "không nằm trong",
    ]
    
    answer_lower = actual_answer.lower()
    
    # Nếu LLM nói "không tìm thấy" → không hallucinate
    for indicator in not_found_indicators:
        if indicator in answer_lower:
            return 0.0
    
    # LLM trả lời bình thường cho câu hỏi unanswerable → hallucination
    return 1.0


# ──────────────────────────────────────────────
# 5. COMPARE COMPLETENESS
# ──────────────────────────────────────────────
def calc_compare_completeness(
    comparison_report: str, 
    expected_changes: List[dict]
) -> float:
    """
    Đo tỷ lệ thay đổi mong đợi được phát hiện trong báo cáo so sánh.
    
    Args:
        comparison_report: Nội dung báo cáo so sánh từ LLM
        expected_changes: Danh sách thay đổi mong đợi
    
    Returns:
        Float 0.0-1.0. 1.0 = phát hiện hết tất cả thay đổi.
    """
    if not expected_changes:
        # Không có thay đổi mong đợi — kiểm tra LLM có nói "không khác biệt" không
        if not comparison_report:
            return 0.0
        no_diff_indicators = [
            "không phát hiện", "giống nhau", "không có sự khác biệt",
            "không thay đổi", "giữ nguyên", "không tìm thấy"
        ]
        report_lower = comparison_report.lower()
        for indicator in no_diff_indicators:
            if indicator in report_lower:
                return 1.0
        return 0.0
    
    report_lower = comparison_report.lower()
    detected = 0
    
    for change in expected_changes:
        change_type = change.get("type", "")
        field = change.get("field", "").lower()
        v1_val = (change.get("v1") or "").lower()
        v2_val = (change.get("v2") or "").lower()
        
        # Kiểm tra xem field hoặc giá trị có xuất hiện trong report không
        is_detected = False
        
        # Check field name (exact)
        if field and field in report_lower:
            is_detected = True
        
        # Check values (exact)
        if v1_val and v1_val in report_lower:
            is_detected = True
        if v2_val and v2_val in report_lower:
            is_detected = True
        
        # Fuzzy: check partial — tách field/value thành từ, kiểm tra từng phần
        if not is_detected:
            # Tách thành các từ > 2 ký tự để fuzzy match
            all_parts = []
            if field:
                all_parts.extend([p.strip() for p in re.split(r'[\s,/]+', field) if len(p.strip()) > 2])
            if v1_val:
                all_parts.extend([p.strip() for p in re.split(r'[\s,/]+', v1_val) if len(p.strip()) > 2])
            if v2_val:
                all_parts.extend([p.strip() for p in re.split(r'[\s,/]+', v2_val) if len(p.strip()) > 2])
            
            # Nếu >= 2 parts xuất hiện trong report → coi là detected
            matched_parts = sum(1 for p in all_parts if p in report_lower)
            if all_parts and matched_parts >= min(2, len(all_parts)):
                is_detected = True
        
        if is_detected:
            detected += 1
    
    return detected / len(expected_changes)


# ──────────────────────────────────────────────
# AGGREGATE METRICS
# ──────────────────────────────────────────────
def aggregate_metrics(results: List[dict]) -> dict:
    """
    Tổng hợp kết quả từ tất cả câu hỏi thành summary metrics.
    
    Bỏ qua các giá trị -1.0 (not applicable).
    """
    metrics_keys = [
        "retrieval_accuracy", 
        "answer_relevance", 
        "citation_accuracy", 
        "hallucination"
    ]
    
    summary = {}
    
    for key in metrics_keys:
        values = [r[key] for r in results if key in r and r[key] >= 0]
        if values:
            summary[key] = {
                "mean": round(sum(values) / len(values), 4),
                "min": round(min(values), 4),
                "max": round(max(values), 4),
                "count": len(values),
            }
        else:
            summary[key] = {"mean": None, "min": None, "max": None, "count": 0}
    
    # Compare completeness (separate because it's from compare_dataset)
    compare_values = [r.get("compare_completeness", -1) for r in results if r.get("compare_completeness", -1) >= 0]
    if compare_values:
        summary["compare_completeness"] = {
            "mean": round(sum(compare_values) / len(compare_values), 4),
            "min": round(min(compare_values), 4),
            "max": round(max(compare_values), 4),
            "count": len(compare_values),
        }
    
    # Overall score (trung bình các mean)
    valid_means = [v["mean"] for v in summary.values() if isinstance(v, dict) and v["mean"] is not None]
    summary["overall_score"] = round(sum(valid_means) / len(valid_means), 4) if valid_means else 0.0
    
    summary["total_questions"] = len(results)
    
    return summary

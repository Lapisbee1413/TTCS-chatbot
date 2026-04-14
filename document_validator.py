"""
document_validator.py – Kiểm tra chất lượng tài liệu pháp lý trước khi ingest

Hỗ trợ:
  - Tiếng Việt + Tiếng Anh
  - Nhiều loại văn bản: Luật, Nghị định, Thông tư, Quyết định, Chỉ thị, 
    Nghị quyết, Công văn, Hợp đồng
  - Cấu trúc chuẩn (Phần/Chương/Mục/Điều/Khoản/Điểm) và cấu trúc phi chuẩn

Phân loại 3 mức:
  - HIGH   (≥70): Accept — văn bản pháp lý rõ ràng
  - MEDIUM (40-69): Warn — có dấu hiệu pháp lý nhưng chưa hoàn chỉnh
  - LOW    (<40): Reject — không phải văn bản pháp lý hoặc quá lộn xộn
"""

import re
from typing import List, Tuple, Optional


# ══════════════════════════════════════════════
# LANGUAGE DETECTION
# ══════════════════════════════════════════════
def detect_language(text: str) -> str:
    """
    Detect ngôn ngữ chính: 'vi', 'en', hoặc 'mixed'.
    Dựa trên tỷ lệ ký tự có dấu tiếng Việt.
    """
    vn_lower = set("àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ")
    vn_chars = vn_lower | {c.upper() for c in vn_lower}

    total_alpha = sum(1 for c in text if c.isalpha())
    if total_alpha == 0:
        return "unknown"

    vn_count = sum(1 for c in text if c in vn_chars)
    vn_ratio = vn_count / total_alpha

    if vn_ratio >= 0.04:
        return "vi"
    elif vn_ratio >= 0.01:
        return "mixed"
    else:
        return "en"


# ══════════════════════════════════════════════
# DOCUMENT TYPE DETECTION
# ══════════════════════════════════════════════

# Loại văn bản và pattern nhận diện
DOCUMENT_TYPES = {
    # ── Văn bản quy phạm chuẩn (có Điều) ──
    "luat": {
        "label": "Luật / Bộ luật",
        "patterns_vi": [r"(?i)\bluật\s+(?:số\s+)?\d+", r"(?i)\bbộ\s+luật\b"],
        "patterns_en": [r"(?i)\b(?:law|act|code)\s+(?:no\.?\s*)?\d+"],
        "has_dieu": True,
        "structure": "standard",
    },
    "nghi_dinh": {
        "label": "Nghị định",
        "patterns_vi": [r"(?i)\bnghị\s+định\s+(?:số\s+)?\d+"],
        "patterns_en": [r"(?i)\bdecree\s+(?:no\.?\s*)?\d+"],
        "has_dieu": True,
        "structure": "standard",
    },
    "thong_tu": {
        "label": "Thông tư",
        "patterns_vi": [r"(?i)\bthông\s+tư\s+(?:số\s+)?\d+"],
        "patterns_en": [r"(?i)\bcircular\s+(?:no\.?\s*)?\d+"],
        "has_dieu": True,
        "structure": "standard",
    },
    "quyet_dinh": {
        "label": "Quyết định",
        "patterns_vi": [r"(?i)\bquyết\s+định\s+(?:số\s+)?\d+", r"(?i)\bquyết\s+định:"],
        "patterns_en": [r"(?i)\bdecision\s+(?:no\.?\s*)?\d+"],
        "has_dieu": True,
        "structure": "standard",
    },
    # ── Văn bản phi chuẩn (có thể không có Điều) ──
    "chi_thi": {
        "label": "Chỉ thị",
        "patterns_vi": [r"(?i)\bchỉ\s+thị\s+(?:số\s+)?\d+"],
        "patterns_en": [r"(?i)\bdirective\s+(?:no\.?\s*)?\d+"],
        "has_dieu": False,
        "structure": "numbered",  # Dùng số 1, 2, 3 hoặc "Một là, Hai là"
    },
    "nghi_quyet": {
        "label": "Nghị quyết",
        "patterns_vi": [r"(?i)\bnghị\s+quyết\s+(?:số\s+)?\d+"],
        "patterns_en": [r"(?i)\bresolution\s+(?:no\.?\s*)?\d+"],
        "has_dieu": False,  # Có thể có hoặc không
        "structure": "mixed",
    },
    "cong_van": {
        "label": "Công văn",
        "patterns_vi": [r"(?i)\bcông\s+văn\s+(?:số\s+)?\d+", r"(?i)\bv/v\b"],
        "patterns_en": [r"(?i)\bofficial\s+(?:letter|dispatch)\b"],
        "has_dieu": False,
        "structure": "freeform",
    },
    # ── Hợp đồng ──
    "hop_dong": {
        "label": "Hợp đồng",
        "patterns_vi": [
            r"(?i)\bhợp\s+đồng\b",
            r"(?i)\bbên\s+[AB]\b",
            r"(?i)\bgiữa\s+.*và\b",
        ],
        "patterns_en": [
            r"(?i)\b(?:contract|agreement)\b",
            r"(?i)\bparty\s+[AB]\b",
            r"(?i)\bbetween\s+.*and\b",
        ],
        "has_dieu": True,
        "structure": "standard",
    },
}


def detect_document_type(text: str, language: str) -> dict:
    """
    Nhận diện loại văn bản dựa trên nội dung.
    Returns: {"type": str, "label": str, "confidence": float, "has_dieu": bool, "structure": str}
    """
    text_lower = text.lower()
    best_match = None
    best_score = 0

    for doc_type, config in DOCUMENT_TYPES.items():
        score = 0
        patterns = config["patterns_vi"] + config["patterns_en"]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                score += len(matches)

        if score > best_score:
            best_score = score
            best_match = doc_type

    if best_match and best_score > 0:
        config = DOCUMENT_TYPES[best_match]
        confidence = min(1.0, best_score / 3.0)  # Normalize
        return {
            "type": best_match,
            "label": config["label"],
            "confidence": round(confidence, 2),
            "has_dieu": config["has_dieu"],
            "structure": config["structure"],
        }

    return {
        "type": "unknown",
        "label": "Không xác định",
        "confidence": 0.0,
        "has_dieu": True,  # Default: expect Điều
        "structure": "unknown",
    }


# ══════════════════════════════════════════════
# LEGAL STRUCTURE PATTERNS
# ══════════════════════════════════════════════

# Cấu trúc phân cấp chuẩn: Phần > Chương > Mục > Điều > Khoản > Điểm
STRUCTURE_PATTERNS_VI = {
    "phan":   r"(?i)(?:\bPhần\s+(?:thứ\s+)?[IVXLC\d]+\b|\bPHẦN\s+[IVXLC\d]+\b)",
    "chuong": r"(?i)(?:\bChương\s+[IVXLC\d]+\b|\bCHƯƠNG\s+[IVXLC\d]+\b)",
    "muc":    r"(?i)\bMục\s+\d+\b",
    "dieu":   r"(?i)\bĐiều\s+\d+",
    "khoan":  r"(?i)\bKhoản\s+\d+",
    "diem":   r"(?i)\b[Đđ]iểm\s+[a-zđ]\b",
}

STRUCTURE_PATTERNS_EN = {
    "part":      r"(?i)\bPart\s+[IVXLC\d]+\b",
    "chapter":   r"(?i)\bChapter\s+[IVXLC\d]+\b",
    "section":   r"(?i)\bSection\s+\d+",
    "article":   r"(?i)\bArticle\s+\d+",
    "clause":    r"(?i)\bClause\s+\d+",
    "paragraph": r"(?i)\bParagraph\s+\d+",
}

# Pattern cho văn bản phi chuẩn (Chỉ thị, Nghị quyết, Công văn)
ALTERNATIVE_STRUCTURE_PATTERNS_VI = {
    "ordinal_words": r"(?i)\b(?:Một là|Hai là|Ba là|Bốn là|Năm là|Sáu là|Bảy là|Tám là|Chín là|Mười là)\b",
    "roman_sections": r"(?m)^[IVXLC]+\.\s+",                          # I. II. III. ở đầu dòng
    "numbered_sections": r"(?m)^\d+\.\s+[A-ZÀ-Ỹ]",                   # 1. Abc ở đầu dòng
    "dash_bullets": r"(?m)^[-–—]\s+",                                  # Gạch đầu dòng
}


# ══════════════════════════════════════════════
# LEGAL KEYWORDS (3 nhóm kinh điển + EN)
# ══════════════════════════════════════════════

LEGAL_KEYWORDS_VI = {
    # Nhóm mở đầu — Phần căn cứ pháp lý (trọng số CAO)
    "preamble": [
        "căn cứ luật", "căn cứ nghị định", "căn cứ thông tư", "căn cứ quyết định",
        "căn cứ bộ luật", "căn cứ pháp lệnh",
        "theo đề nghị của", "xét đề nghị", "theo quy định",
        "quyết định:", "nay ban hành", "ban hành kèm theo",
        "chính phủ", "quốc hội", "thủ tướng",
    ],
    # Nhóm quy định chung (trọng số TRUNG BÌNH)
    "general_provisions": [
        "phạm vi điều chỉnh", "đối tượng áp dụng", "giải thích từ ngữ",
        "nguyên tắc", "định nghĩa", "phạm vi áp dụng",
    ],
    # Nhóm kết thúc (trọng số TRUNG BÌNH)
    "closing": [
        "hiệu lực thi hành", "trách nhiệm thi hành", "tổ chức thực hiện",
        "điều khoản thi hành", "điều khoản chuyển tiếp",
        "nơi nhận:", "nơi nhận :",
    ],
    # Nhóm từ khóa nội dung pháp lý chung (trọng số THẤP)
    "general_legal": [
        "hợp đồng", "bên a", "bên b", "nghĩa vụ", "trách nhiệm",
        "quyền lợi", "quyền hạn", "điều khoản", "cam kết", "thỏa thuận",
        "vi phạm", "bồi thường", "chấm dứt", "thanh toán", "phạt",
        "bảo hành", "hiệu lực", "ký kết", "thời hạn", "pháp luật",
        "quy định", "phụ lục", "nghị định", "thông tư", "luật",
        "giấy phép", "chứng nhận", "giải quyết", "tranh chấp",
        "xử phạt", "hành chính", "dân sự", "hình sự",
        "cơ quan", "tổ chức", "cá nhân",
    ],
}

LEGAL_KEYWORDS_EN = {
    "preamble": [
        "pursuant to", "in accordance with", "by virtue of",
        "whereas", "hereby", "enacted by", "be it enacted",
        "effective date", "promulgated",
    ],
    "general_provisions": [
        "scope of application", "subject of regulation", "definitions",
        "interpretation", "general provisions", "preliminary",
    ],
    "closing": [
        "implementation", "enforcement", "transitional provisions",
        "entry into force", "effective upon", "final provisions",
    ],
    "general_legal": [
        "contract", "agreement", "party", "obligation", "liability",
        "rights", "clause", "provision", "breach", "compensation",
        "termination", "payment", "warranty", "jurisdiction",
        "governing law", "dispute resolution", "indemnity",
        "force majeure", "confidentiality", "amendment",
        "article", "section", "regulation", "statute",
    ],
}


# ══════════════════════════════════════════════
# MAIN VALIDATION FUNCTION
# ══════════════════════════════════════════════
def validate_legal_document(text: str) -> dict:
    """
    Đánh giá chất lượng tài liệu pháp lý.
    Tự động detect ngôn ngữ và loại văn bản, áp dụng tiêu chí phù hợp.

    Returns:
        dict: {
            "quality": "HIGH" | "MEDIUM" | "LOW",
            "score": 0-100,
            "language": "vi" | "en" | "mixed",
            "document_type": {...},
            "checks": [...],
            "summary": "...",
            "recommendation": "accept" | "warn" | "reject",
        }
    """
    checks = []
    text = text.strip()

    # ── Detect language & document type ──
    language = detect_language(text)
    doc_type = detect_document_type(text, language)

    # ── Check 1: Độ dài tối thiểu ──
    checks.append(_check_text_length(text))

    # ── Check 2: Ngôn ngữ (VN hoặc EN đều OK, unknown = xấu) ──
    checks.append(_check_language(text, language))

    # ── Check 3: Tỷ lệ ký tự có nghĩa ──
    checks.append(_check_meaningful_chars(text))

    # ── Check 4: Cấu trúc pháp lý (theo ngôn ngữ + loại VB) ──
    checks.append(_check_legal_structure(text, language, doc_type))

    # ── Check 5: Thứ tự hợp lý ──
    checks.append(_check_article_order(text, language))

    # ── Check 6: Từ khóa pháp lý (3 nhóm, theo ngôn ngữ) ──
    checks.append(_check_legal_keywords(text, language))

    # ── Check 7: Loại văn bản có nhận diện được không ──
    checks.append(_check_document_type(doc_type))

    # ── Tính điểm tổng ──
    total_score = sum(c["score"] * c["weight"] for c in checks)
    total_weight = sum(c["weight"] for c in checks)
    final_score = round(total_score / total_weight) if total_weight > 0 else 0

    # ── Phân loại ──
    if final_score >= 70:
        quality = "HIGH"
        summary = f"Tài liệu pháp lý [{doc_type['label']}] ({language.upper()}) có cấu trúc rõ ràng."
        recommendation = "accept"
    elif final_score >= 40:
        quality = "MEDIUM"
        summary = f"Tài liệu [{doc_type['label']}] ({language.upper()}) có dấu hiệu pháp lý nhưng chưa hoàn chỉnh."
        recommendation = "warn"
    else:
        quality = "LOW"
        failed_checks = [c for c in checks if c["score"] < 50]
        reasons = [c["reason"] for c in failed_checks[:3]]
        summary = "Tài liệu không đạt yêu cầu. " + " | ".join(reasons)
        recommendation = "reject"

    return {
        "quality": quality,
        "score": final_score,
        "language": language,
        "document_type": doc_type,
        "checks": checks,
        "summary": summary,
        "recommendation": recommendation,
    }


# ══════════════════════════════════════════════
# INDIVIDUAL CHECKS
# ══════════════════════════════════════════════

def _check_text_length(text: str) -> dict:
    """Check 1: Văn bản phải đủ dài."""
    length = len(text)

    if length >= 1000:
        score, reason = 100, f"Đủ dài ({length:,} ký tự)"
    elif length >= 500:
        score, reason = 70, f"Hơi ngắn ({length:,} ký tự)"
    elif length >= 200:
        score, reason = 40, f"Quá ngắn ({length:,} ký tự)"
    else:
        score, reason = 0, f"Quá ngắn ({length:,} ký tự) — không đủ nội dung"

    return {"name": "text_length", "label": "Độ dài văn bản", "score": score,
            "weight": 1.0, "reason": reason, "detail": {"length": length}}


def _check_language(text: str, language: str) -> dict:
    """
    Check 2: Ngôn ngữ — tiếng Việt HOẶC tiếng Anh đều hợp lệ.
    Chỉ penalize nếu không detect được ngôn ngữ nào.
    """
    if language == "vi":
        score, reason = 100, "Tiếng Việt"
    elif language == "en":
        score, reason = 100, "Tiếng Anh (English)"
    elif language == "mixed":
        score, reason = 80, "Song ngữ (Việt-Anh)"
    else:
        # Kiểm tra xem có chữ cái nào không
        alpha_count = sum(1 for c in text if c.isalpha())
        if alpha_count > 0:
            score, reason = 40, "Không xác định được ngôn ngữ"
        else:
            score, reason = 0, "Không phát hiện chữ cái nào"

    return {"name": "language", "label": "Ngôn ngữ", "score": score,
            "weight": 1.0, "reason": reason, "detail": {"language": language}}


def _check_meaningful_chars(text: str) -> dict:
    """Check 3: Tỷ lệ ký tự có nghĩa vs ký tự rác."""
    if not text:
        return {"name": "meaningful_chars", "label": "Ký tự có nghĩa", "score": 0,
                "weight": 1.0, "reason": "Văn bản rỗng", "detail": {"ratio": 0}}

    meaningful = sum(1 for c in text if c.isalnum() or c in ' .,;:!?()[]{}"-/\n\r\t\'')
    ratio = meaningful / len(text)

    if ratio >= 0.85:
        score, reason = 100, f"Nội dung sạch ({ratio:.0%} ký tự có nghĩa)"
    elif ratio >= 0.7:
        score, reason = 60, f"Có ít ký tự rác ({ratio:.0%})"
    else:
        score, reason = 20, f"Nhiều ký tự rác ({ratio:.0%}) — có thể lỗi encoding"

    return {"name": "meaningful_chars", "label": "Ký tự có nghĩa", "score": score,
            "weight": 1.0, "reason": reason, "detail": {"ratio": round(ratio, 4)}}


def _check_legal_structure(text: str, language: str, doc_type: dict) -> dict:
    """
    Check 4: Kiểm tra cấu trúc pháp lý.
    
    Logic:
    - Nếu VB chuẩn (Luật/NĐ/TT/HĐ): tìm Phần/Chương/Mục/Điều/Khoản/Điểm
    - Nếu VB phi chuẩn (CT/NQ/CV): tìm cấu trúc thay thế (số thứ tự, gạch đầu dòng)
    - Hỗ trợ cả VN và EN patterns
    """
    counts = {}
    structure_type = doc_type.get("structure", "unknown")

    # ── Count cấu trúc chuẩn (VN) ──
    for key, pattern in STRUCTURE_PATTERNS_VI.items():
        counts[f"vi_{key}"] = len(re.findall(pattern, text))

    # ── Count cấu trúc chuẩn (EN) ──
    for key, pattern in STRUCTURE_PATTERNS_EN.items():
        counts[f"en_{key}"] = len(re.findall(pattern, text))

    # ── Count cấu trúc phi chuẩn ──
    for key, pattern in ALTERNATIVE_STRUCTURE_PATTERNS_VI.items():
        counts[f"alt_{key}"] = len(re.findall(pattern, text))

    # Tổng hợp theo nhóm
    standard_vi = counts.get("vi_dieu", 0) + counts.get("vi_khoan", 0) + counts.get("vi_chuong", 0)
    standard_en = counts.get("en_article", 0) + counts.get("en_clause", 0) + counts.get("en_chapter", 0) + counts.get("en_section", 0)
    alternative = counts.get("alt_ordinal_words", 0) + counts.get("alt_roman_sections", 0) + counts.get("alt_numbered_sections", 0)

    total_standard = standard_vi + standard_en
    total_all = total_standard + alternative

    # ── Scoring ──
    if total_standard >= 8:
        score = 100
        detail_parts = []
        if counts.get("vi_dieu", 0) > 0:
            detail_parts.append(f"{counts['vi_dieu']} Điều")
        if counts.get("vi_khoan", 0) > 0:
            detail_parts.append(f"{counts['vi_khoan']} Khoản")
        if counts.get("vi_chuong", 0) > 0:
            detail_parts.append(f"{counts['vi_chuong']} Chương")
        if counts.get("en_article", 0) > 0:
            detail_parts.append(f"{counts['en_article']} Article")
        if counts.get("en_section", 0) > 0:
            detail_parts.append(f"{counts['en_section']} Section")
        if counts.get("en_clause", 0) > 0:
            detail_parts.append(f"{counts['en_clause']} Clause")
        reason = f"Cấu trúc rõ ràng ({', '.join(detail_parts)})"
    elif total_standard >= 3:
        score = 75
        reason = f"Có cấu trúc ({total_standard} markers chuẩn)"
    elif total_standard >= 1:
        score = 50
        reason = f"Ít cấu trúc chuẩn ({total_standard} markers)"
    elif alternative >= 5:
        # Văn bản phi chuẩn nhưng có cấu trúc thay thế
        score = 65
        reason = f"Cấu trúc phi chuẩn ({alternative} markers thay thế: số thứ tự, gạch đầu dòng)"
    elif alternative >= 2:
        score = 40
        reason = f"Ít cấu trúc ({alternative} markers phi chuẩn)"
    elif total_all > 0:
        score = 25
        reason = f"Rất ít cấu trúc ({total_all} markers tổng)"
    else:
        score = 0
        reason = "Không tìm thấy cấu trúc pháp lý nào (VN/EN)"

    return {"name": "legal_structure", "label": "Cấu trúc pháp lý", "score": score,
            "weight": 3.0, "reason": reason, "detail": counts}


def _check_article_order(text: str, language: str) -> dict:
    """
    Check 5: Thứ tự hợp lý.
    Kiểm tra Điều (VN) / Article (EN) / Phần (Roman) theo thứ tự tăng dần.
    """
    # Tìm tất cả số Điều (VN)
    vi_matches = [int(m) for m in re.findall(r"(?i)Điều\s+(\d+)", text)]
    # Tìm tất cả Article (EN)
    en_matches = [int(m) for m in re.findall(r"(?i)Article\s+(\d+)", text)]
    # Tìm Section (EN)
    en_sections = [int(m) for m in re.findall(r"(?i)Section\s+(\d+)", text)]

    # Chọn sequence dài nhất
    numbers = vi_matches if len(vi_matches) >= len(en_matches) else en_matches
    if len(en_sections) > len(numbers):
        numbers = en_sections

    if len(numbers) < 2:
        return {"name": "article_order", "label": "Thứ tự điều khoản", "score": 50,
                "weight": 1.5, "reason": f"Chỉ có {len(numbers)} mục — không đủ để kiểm tra",
                "detail": {"articles_found": numbers}}

    # Kiểm tra thứ tự
    out_of_order = sum(1 for i in range(1, len(numbers)) if numbers[i] < numbers[i - 1])
    total_transitions = len(numbers) - 1
    order_ratio = 1.0 - (out_of_order / total_transitions) if total_transitions > 0 else 1.0

    # Unique sorted check
    unique_nums = list(dict.fromkeys(numbers))
    is_sorted = unique_nums == sorted(unique_nums)

    if order_ratio >= 0.9 and is_sorted:
        score = 100
        reason = f"Thứ tự tốt ({numbers[0]}→{numbers[-1]}, {len(set(numbers))} mục)"
    elif order_ratio >= 0.7:
        score = 60
        reason = f"Thứ tự chấp nhận ({order_ratio:.0%} đúng, {out_of_order} lần lộn)"
    elif order_ratio >= 0.5:
        score = 30
        reason = f"Lộn xộn ({out_of_order}/{total_transitions} sai thứ tự)"
    else:
        score = 10
        reason = f"Rất lộn xộn ({out_of_order}/{total_transitions} sai) — 'điều lộn khoản'"

    return {"name": "article_order", "label": "Thứ tự điều khoản", "score": score,
            "weight": 1.5, "reason": reason,
            "detail": {"articles_found": numbers[:20], "order_ratio": round(order_ratio, 4)}}


def _check_legal_keywords(text: str, language: str) -> dict:
    """
    Check 6: Từ khóa pháp lý 3 nhóm (mở đầu, quy định chung, kết thúc) + chung.
    Trọng số: preamble (×3) > closing (×2) > general_provisions (×2) > general_legal (×1)
    """
    text_lower = text.lower()

    # Chọn bộ keywords theo ngôn ngữ
    if language == "en":
        kw_sets = LEGAL_KEYWORDS_EN
    elif language == "mixed":
        # Merge cả 2
        kw_sets = {}
        for group in LEGAL_KEYWORDS_VI:
            kw_sets[group] = LEGAL_KEYWORDS_VI[group] + LEGAL_KEYWORDS_EN.get(group, [])
    else:
        kw_sets = LEGAL_KEYWORDS_VI

    # Đếm theo nhóm
    group_scores = {}
    found_all = []
    
    group_weights = {"preamble": 3.0, "general_provisions": 2.0, "closing": 2.0, "general_legal": 1.0}

    for group, keywords in kw_sets.items():
        found_in_group = [kw for kw in keywords if kw in text_lower]
        ratio = len(found_in_group) / len(keywords) if keywords else 0
        group_scores[group] = {
            "found": len(found_in_group),
            "total": len(keywords),
            "ratio": round(ratio, 4),
            "weight": group_weights.get(group, 1.0),
        }
        found_all.extend(found_in_group)

    # Tính weighted score
    weighted_sum = 0
    weight_sum = 0
    for group, data in group_scores.items():
        w = data["weight"]
        # Map ratio to 0-100 score
        if data["ratio"] >= 0.2:
            s = 100
        elif data["ratio"] >= 0.1:
            s = 70
        elif data["ratio"] >= 0.05:
            s = 40
        elif data["found"] >= 1:
            s = 20
        else:
            s = 0
        weighted_sum += s * w
        weight_sum += w

    final = round(weighted_sum / weight_sum) if weight_sum > 0 else 0
    found_unique = list(dict.fromkeys(found_all))

    if final >= 70:
        reason = f"Nhiều từ khóa pháp lý ({len(found_unique)}): {', '.join(found_unique[:6])}..."
    elif final >= 40:
        reason = f"Có từ khóa pháp lý ({len(found_unique)}): {', '.join(found_unique[:5])}"
    elif len(found_unique) > 0:
        reason = f"Ít từ khóa pháp lý ({len(found_unique)}): {', '.join(found_unique)}"
    else:
        reason = "Không tìm thấy từ khóa pháp lý nào"

    return {"name": "legal_keywords", "label": "Từ khóa pháp lý", "score": final,
            "weight": 2.0, "reason": reason,
            "detail": {"groups": group_scores, "found_sample": found_unique[:10]}}


def _check_document_type(doc_type: dict) -> dict:
    """Check 7: Loại văn bản có nhận diện được không."""
    if doc_type["type"] == "unknown":
        return {"name": "document_type", "label": "Loại văn bản", "score": 20,
                "weight": 1.5, "reason": "Không nhận diện được loại văn bản",
                "detail": doc_type}

    conf = doc_type["confidence"]
    if conf >= 0.7:
        score = 100
    elif conf >= 0.3:
        score = 70
    else:
        score = 50

    reason = f"Nhận diện: {doc_type['label']} (confidence={conf:.0%})"
    return {"name": "document_type", "label": "Loại văn bản", "score": score,
            "weight": 1.5, "reason": reason, "detail": doc_type}


# ══════════════════════════════════════════════
# UTILITY
# ══════════════════════════════════════════════
def format_validation_report(result: dict) -> str:
    """Format kết quả validation thành text cho console/UI."""
    lines = []

    quality = result["quality"]
    score = result["score"]
    lang = result.get("language", "?")
    doc_type = result.get("document_type", {}).get("label", "?")

    emoji = {"HIGH": "✅", "MEDIUM": "⚠️", "LOW": "❌"}.get(quality, "?")

    lines.append(f"\n{'='*55}")
    lines.append(f"{emoji} CHẤT LƯỢNG: {quality} ({score}/100) | {lang.upper()} | {doc_type}")
    lines.append(f"{'='*55}")
    lines.append(f"📋 {result['summary']}")
    lines.append(f"\n{'─'*55}")
    lines.append(f"CHI TIẾT KIỂM TRA:")
    lines.append(f"{'─'*55}")

    for check in result["checks"]:
        check_emoji = "✅" if check["score"] >= 70 else "⚠️" if check["score"] >= 40 else "❌"
        weight_str = f"(×{check['weight']:.1f})" if check["weight"] != 1.0 else ""
        lines.append(f"  {check_emoji} {check['label']:20s} {check['score']:3d}/100 {weight_str}")
        lines.append(f"     └─ {check['reason']}")

    lines.append(f"{'='*55}\n")

    return "\n".join(lines)

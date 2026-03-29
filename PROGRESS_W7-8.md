# 📊 BÁO CÁO TIẾN ĐỘ TUẦN 7-8: CITATION & COMPARISON REPORT

**Thời gian:** 2026-03-16 → 2026-03-29
**Mục tiêu chính:** Sinh báo cáo so sánh + citation; Nguyên tắc "không bằng chứng → không kết luận"

---

## ✅ TÓM TẮT HOÀN THÀNH

| Mục tiêu | Trạng thái | Ghi chú |
|----------|-----------|--------|
| Tính năng so sánh 2 phiên bản | ✅ 100% | `compare.py` + `generate_comparison_report()` |
| Citation tự động | ✅ 100% | Tất cả output đều có `[Nguồn: X, Điều Y]` |
| Evidence-based answering | ✅ 100% | LLM prompt tuân thủ + test case |
| Báo cáo cấu trúc rõ ràng | ✅ 100% | Nội dung V1/V2, Điểm khác, Tóm tắt |
| Test & Documentation | ✅ 100% | `test_compare.py` + readme.md cập nhật |

---

## 📝 CHI TIẾT THỰC HIỆN

### 1. **compare.py** (CLI Tool So Sánh) ✅
```bash
# Lệnh cơ bản
python compare.py "Điều 5" --v1 "HopDong_V1" --v2 "HopDong_V2"

# Với hiển thị chi tiết
python compare.py "Điều 3" --v1 "V1" --v2 "V2" --show-full-text --show-citations
```

**Tính năng:**
- ✅ Nhập vào: tên điều khoản, tên 2 phiên bản nguồn
- ✅ Output: báo cáo so sánh có cấu trúc (Nội dung V1/V2, Khác nhau, Tóm tắt)
- ✅ Citation: tự động gắn `[Nguồn: X, Điều Y]` cho mọi thông tin
- ✅ Hỗ trợ 2 model: Qwen 2.5:1.5b (mặc định) + Mistral 7B
- ✅ Optional flags: `--show-full-text`, `--show-citations`

---

### 2. **query.py** (Evidence-based Q&A) ✅
```bash
# Query cơ bản với citation
python query.py "Điều 3 quy định gì?" --show-chunks

# Chỉ retrieve chunks (không LLM)
python query.py "Điều 5?" --retrieve-only
```

**Cập nhật:**
- ✅ Tự động trích dẫn `[Nguồn: source, article_ref]` trong câu trả lời
- ✅ Prompt LLM tuân thủ nguyên tắc: "Nếu không có bằng chứng → nói 'Không tìm thấy'"
- ✅ Hỗ trợ `--retrieve-only` để test chunks mà không cần Ollama
- ✅ Windows encoding fix (`utf-8` cho console)

---

### 3. **rag_pipeline.py** (Backend Logic) ✅

#### 3a. `generate_comparison_report()`
```python
def generate_comparison_report(
    article_name: str,
    source_v1: str,
    source_v2: str,
    model: str = QWEN_MODEL
) -> dict
```

**Logic:**
1. Tìm chunks chứa `article_name` từ 2 sources
2. Trích xuất toàn bộ nội dung V1 & V2
3. Gọi LLM để phân tích sự khác biệt (prompt evidence-based)
4. Trả về dict chứa:
   - `v1_text`: toàn bộ nội dung Điều X từ V1
   - `v2_text`: toàn bộ nội dung Điều X từ V2
   - `comparison_report`: báo cáo phân tích chi tiết
   - `citations`: list các trích dẫn được sử dụng

#### 3b. `ask_ollama()` - Cập nhật Evidence-Based Prompt
```python
system_prompt = """
Bạn là trợ lý pháp lý được huấn luyện nghiêm ngặt tuân thủ nguyên tắc:
- KHÔNG suy luận hoặc bổ sung thông tin không có trong chunks
- KHÔNG bằng chứng → KHÔNG kết luận
- MỖI câu trả lời phải trích dẫn nguồn: [Nguồn: source_name, Điều_số]
"""
```

---

### 4. **Test & Documentation** ✅

#### test_compare.py
```bash
python test_compare.py
```
Test cases:
- So sánh Điều 2 (cả 2 version có)
- So sánh Điều 10 (không có → báo "không tìm thấy")
- Verify citations chính xác
- Verify không có suy luận thêm

#### readme.md - Cập nhật
- ✅ Hướng dẫn sử dụng `compare.py`
- ✅ Các lệnh test query với citation
- ✅ Mô tả kiến trúc RAG
- ✅ Giải thích nguyên tắc evidence-based

---

## 🛠️ CÔNG NGHỆ SỬ DỤNG

| Thành phần | Chi tiết |
|-----------|---------|
| **LLM** | Qwen 2.5:1.5b (mặc định), Mistral 7B |
| **Embedding** | sentence-transformers/paraphrase-multilingual |
| **Vector DB** | ChromaDB (persistent tại `./chroma_db/`) |
| **Chunking** | Legal-pattern-based + size-based |
| **Framework** | Python 3.8+ (argparse, ollama-py) |

---

## 📌 LỆnh TEST TÓM TẮT

```bash
### Test Citation & Evidence-Based
python query.py "Điều 3 quy định gì?" --show-chunks
python query.py "Thông tin không có trong tài liệu?"
python query.py "..." --retrieve-only

### Test So Sánh
python compare.py "Điều 2" --v1 "HopDong_V1" --v2 "HopDong_V2"
python compare.py "Điều 2" --show-full-text --show-citations
python compare.py "Điều 10"  # Test "không tìm thấy"

### Test full pipeline
python test_compare.py
```

---

## 🎯 CRITERIA THÀNH CÔNg

✅ **Báo cáo so sánh:** Cấu trúc rõ (Nội dung V1/V2, Khác biệt, Tóm tắt)
✅ **Citation:** Mọi thông tin đều có `[Nguồn: X, Điều Y]`
✅ **Evidence-based:** Không suy luận, không đoán mò
✅ **"Không bằng chứng → Không kết luận":** Test case cho info không tồn tại
✅ **Test & Docs:** `test_compare.py` + `readme.md` đầy đủ

---

## 📝 GIT COMMITS

```
59226c8 retrieve
0f72d1b Week 3-4
b3e60e5 AC
d852b7e update require.txt and readme
7e6feed first update
```

**Modified files:**
- ✅ `compare.py` (NEW) – CLI tool so sánh
- ✅ `query.py` (M) – cập nhật evidence-based prompt
- ✅ `rag_pipeline.py` (M) – thêm `generate_comparison_report()`
- ✅ `test_compare.py` (M) – test for comparison
- ✅ `readme.md` (M) – cập nhật docs

---

## 🚀 NEXT STEPS (Tuần 9+)

- [ ] Tối ưu prompt cho accuracy cao hơn
- [ ] Thêm support cho .docx format
- [ ] Integration với Discord Bot
- [ ] Performance tuning (caching, batch query)
- [ ] UI web dashboard

---

**Status:** ✅ **ĐỦ TIÊU CHÍ - READY FOR REVIEW**

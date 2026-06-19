"""
RAG Pipeline – PDF → Chunking → ChromaDB → Q&A
Models  : Qwen 2.5 (3B) and/or Mistral 7B via Ollama (local)
Embeddings: sentence-transformers (local)

Week 11: Cải tiến chất lượng
  - Hierarchical chunking with context prefix
  - Source-aware retrieval + distance threshold
  - Few-shot anti-hallucination prompt
  - Fuzzy source matching for compare
  - Faithfulness post-processing
"""

import os

# ── Force offline mode: dùng model đã cache, không cần mạng ──
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import re
import uuid
from collections import defaultdict
from typing import List, Optional, Set
import docx

import chromadb
from chromadb.config import Settings
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

# ──────────────────────────────────────────────
# 1. CONFIGURATION
# ──────────────────────────────────────────────
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = "pdf_rag"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"  # multilingual, ~120 MB
CHUNK_SIZE = 500        # characters per chunk
CHUNK_OVERLAP = 100     # overlap between consecutive chunks

# Ollama model names (make sure they are pulled: `ollama pull qwen2.5:3b` / `ollama pull mistral`)
QWEN_MODEL    = "qwen2.5:3b"
MISTRAL_MODEL = "mistral"

# Retrieval config
DEFAULT_TOP_K = 5
CROSS_DOC_TOP_K = 8     # Top-K cho câu hỏi cross-document (không có source cụ thể)
DISTANCE_THRESHOLD = 0.95  # Cosine distance > this = too far, discard
RETRIEVAL_CANDIDATE_MULTIPLIER = 4
CROSS_DOC_MAX_PER_SOURCE = 2

# Source name aliases — để fuzzy match giữa dataset names và các tên khác
SOURCE_ALIASES = {
    "thuenha_v1": "ThueNha_V1",
    "thuenha_v2": "ThueNha_V2",
    "hopdong_thue_nha_v1": "ThueNha_V1",
    "hopdong_thue_nha_v2": "ThueNha_V2",
    "hopdong_v1": "HopDong_V1",
    "hopdong_v2": "HopDong_V2",
    "phuluc_v1": "PhuLuc_V1",
    "phuluc_v2": "PhuLuc_V2",
    "phuluc_kho_v1": "PhuLuc_V1",
    "phuluc_kho_v2": "PhuLuc_V2",
    "dichvu_baotri": "DichVu_BaoTri",
    "hopdong_dichvu_baotri": "DichVu_BaoTri",
    "laodong": "LaoDong",
    "hopdong_laodong": "LaoDong",
    "muaban_thietbi": "MuaBan_ThietBi",
    "hopdong_muaban_thietbi": "MuaBan_ThietBi",
}

# ──────────────────────────────────────────────
# 2. EMBEDDING HELPER
# ──────────────────────────────────────────────
_embed_model: Optional[SentenceTransformer] = None


def get_embed_model() -> SentenceTransformer:
    global _embed_model
    if _embed_model is None:
        print(f"[RAG] Loading embedding model: {EMBEDDING_MODEL}")
        _embed_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embed_model


def embed_texts(texts: List[str]) -> List[List[float]]:
    model = get_embed_model()
    return model.encode(texts, show_progress_bar=False).tolist()


# ──────────────────────────────────────────────
# 3. CHROMADB HELPER
# ──────────────────────────────────────────────
_chroma_client: Optional[chromadb.PersistentClient] = None
_collection = None


def get_collection():
    global _chroma_client, _collection
    if _chroma_client is None:
        os.makedirs(CHROMA_DB_PATH, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    if _collection is None:
        _collection = _chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def list_available_sources() -> dict:
    """Liệt kê tất cả sources và số chunks trong ChromaDB (debug helper)."""
    collection = get_collection()
    all_data = collection.get(include=["metadatas"])
    sources = {}
    for meta in all_data["metadatas"]:
        src = meta.get("source", "Unknown")
        sources[src] = sources.get(src, 0) + 1
    return sources


def normalize_source_name(name: str) -> str:
    """Chuẩn hóa source name qua alias table."""
    key = name.lower().strip().replace(" ", "_").replace("-", "_")
    return SOURCE_ALIASES.get(key, name)


# ──────────────────────────────────────────────
# 4. DOCUMENT READING (Hỗ trợ PDF & DOCX)
# ──────────────────────────────────────────────
def read_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    pages_text = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages_text)

def read_docx(docx_path: str) -> str:
    """Hàm đọc file DOCX"""
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def read_document(file_path: str) -> str:
    """Tự động nhận diện đuôi file"""
    ext = file_path.lower().split('.')[-1]
    if ext == 'pdf':
        text = read_pdf(file_path)
    elif ext == 'docx':
        text = read_docx(file_path)
    else:
        raise ValueError(f"Định dạng .{ext} chưa được hỗ trợ. Vui lòng dùng PDF hoặc DOCX.")
    
    print(f"[RAG] Đã trích xuất {len(text):,} ký tự từ {file_path}.")
    return text

# ──────────────────────────────────────────────
# 5. CHUNKING (Hierarchical Chunking cho Luật)
# ──────────────────────────────────────────────

def _detect_chapter_context(text: str) -> List[dict]:
    """
    Tìm các header cấp cao (Chương/Phần/Mục) và vị trí trong text.
    Dùng để gắn context cho mỗi Điều.
    """
    contexts = []
    # Tìm Chương
    for match in re.finditer(r"(?i)(Chương\s+[IVXLC\d]+[^\n]*)", text):
        contexts.append({
            "type": "chapter",
            "label": match.group(1).strip(),
            "pos": match.start()
        })
    # Tìm Phần
    for match in re.finditer(r"(?i)(Phần\s+(?:thứ\s+)?[IVXLC\d]+[^\n]*)", text):
        contexts.append({
            "type": "part",
            "label": match.group(1).strip(),
            "pos": match.start()
        })
    # Tìm Mục
    for match in re.finditer(r"(?i)(Mục\s+\d+[^\n]*)", text):
        contexts.append({
            "type": "section",
            "label": match.group(1).strip(),
            "pos": match.start()
        })
    
    # Sắp xếp theo vị trí
    contexts.sort(key=lambda x: x["pos"])
    return contexts


def _get_parent_context(pos: int, chapter_contexts: List[dict]) -> str:
    """
    Tìm header cha gần nhất (Chương/Phần/Mục) cho một vị trí trong text.
    Trả về string prefix: "[Chương II: Quyền và nghĩa vụ]"
    """
    parent = None
    for ctx in chapter_contexts:
        if ctx["pos"] <= pos:
            parent = ctx
        else:
            break
    
    if parent:
        return f"[{parent['label']}]"
    return ""


def chunk_legal_text(text: str, min_chunk_size: int = 50, max_chunk_size: int = 2000) -> List[dict]:
    """
    Chia đoạn dựa trên cấu trúc "Điều X" — Hierarchical Chunking.
    
    Cải tiến Week 11:
    1. Gắn parent context (Chương/Phần/Mục) vào mỗi chunk
    2. Sub-chunking: Điều quá dài → tách theo Khoản, giữ header
    3. Fallback: sliding window nếu không có cấu trúc "Điều"
    
    Args:
        text: Văn bản cần chia
        min_chunk_size: Kích thước tối thiểu chunk (chars). Chunks nhỏ hơn bị loại.
        max_chunk_size: Kích thước tối đa chunk. Quá dài → sub-split theo Khoản.
    """
    # Chuẩn hóa khoảng trắng
    text = re.sub(r"\n{3,}", "\n\n", text.strip())

    # Detect cấu trúc cấp cao
    chapter_contexts = _detect_chapter_context(text)

    # Regex tìm điểm chia: "Điều" + Số
    pattern = r"(?i)(?=\bĐiều\s+\d+[\.\:])"
    
    # Tìm vị trí tất cả các "Điều"
    splits = list(re.finditer(pattern, text))
    
    # ── Fallback: Sliding window nếu không tìm thấy "Điều" ──
    if len(splits) < 2:
        print(f"[RAG] Không tìm thấy cấu trúc 'Điều' — dùng sliding window fallback")
        return _chunk_sliding_window(text, min_chunk_size=min_chunk_size)

    # ── Split theo "Điều" ──
    raw_chunks = re.split(pattern, text)
    chunks_with_meta = []

    for i, chunk in enumerate(raw_chunks):
        chunk = chunk.strip()
        if len(chunk) < min_chunk_size:
            continue

        # Tìm Điều mấy + chuẩn hóa article_ref
        match = re.match(r"(?i)(Điều\s+\d+)", chunk)
        if match:
            article_ref = match.group(1)
            # Normalize: "điều 3" → "Điều 3", "ĐIỀU 3" → "Điều 3"
            article_ref = re.sub(r'[.:;]\s*$', '', article_ref.strip())
            article_ref = article_ref.title()
        else:
            article_ref = "Thông tin chung"

        # Tìm parent context (Chương/Phần/Mục)
        # Ước tính vị trí chunk trong text gốc
        chunk_pos = text.find(chunk[:50]) if len(chunk) >= 50 else 0
        parent_ctx = _get_parent_context(chunk_pos, chapter_contexts)

        # ── Sub-chunking nếu quá dài ──
        if len(chunk) > max_chunk_size:
            sub_chunks = _sub_chunk_by_khoan(chunk, article_ref, parent_ctx, max_chunk_size)
            chunks_with_meta.extend(sub_chunks)
        else:
            # Thêm context prefix vào text
            prefixed_text = f"{parent_ctx} {chunk}".strip() if parent_ctx else chunk
            
            chunks_with_meta.append({
                "text": prefixed_text,
                "metadata": {
                    "article_ref": article_ref,
                    "parent_context": parent_ctx,
                }
            })

    # Fallback nếu không có chunk hợp lệ
    if not chunks_with_meta:
        print(f"[RAG] [WARNING] Không tìm thấy chunk hợp lệ — giữ lại toàn bộ văn bản.")
        chunks_with_meta.append({
            "text": text,
            "metadata": {"article_ref": "Toàn bộ tài liệu", "parent_context": ""}
        })

    print(f"[RAG] Đã tạo {len(chunks_with_meta)} chunks theo cấu trúc Điều khoản (lọc < {min_chunk_size} chars, sub-split > {max_chunk_size} chars).")
    return chunks_with_meta


def _sub_chunk_by_khoan(chunk: str, article_ref: str, parent_ctx: str, max_size: int) -> List[dict]:
    """
    Tách 1 Điều dài thành nhiều sub-chunk theo Khoản.
    Mỗi sub-chunk giữ header "Điều X" ở đầu.
    """
    # Tìm header (dòng đầu tiên chứa "Điều X")
    header_match = re.match(r"(?i)(Điều\s+\d+[^\n]*\n?)", chunk)
    header = header_match.group(1) if header_match else ""
    body = chunk[len(header):] if header else chunk

    # Tách theo Khoản
    khoan_pattern = r"(?=(?:^|\n)\s*\d+\.\s)"
    parts = re.split(khoan_pattern, body)

    sub_chunks = []
    current_text = header.strip()

    for part in parts:
        part = part.strip()
        if not part:
            continue

        if len(current_text) + len(part) > max_size and len(current_text) > 100:
            # Lưu chunk hiện tại
            prefixed = f"{parent_ctx} {current_text}".strip() if parent_ctx else current_text
            sub_chunks.append({
                "text": prefixed,
                "metadata": {
                    "article_ref": article_ref,
                    "parent_context": parent_ctx,
                }
            })
            current_text = f"{header.strip()}\n{part}" if header else part
        else:
            current_text = f"{current_text}\n{part}" if current_text else part

    # Lưu phần còn lại
    if current_text.strip():
        prefixed = f"{parent_ctx} {current_text}".strip() if parent_ctx else current_text.strip()
        sub_chunks.append({
            "text": prefixed,
            "metadata": {
                "article_ref": article_ref,
                "parent_context": parent_ctx,
            }
        })

    return sub_chunks


def _chunk_sliding_window(text: str, chunk_size: int = 500, overlap: int = 100, min_chunk_size: int = 50) -> List[dict]:
    """
    Fallback: chia đoạn bằng sliding window khi không có cấu trúc 'Điều'.
    Dùng cho công văn, chỉ thị, nghị quyết, v.v.
    """
    chunks_with_meta = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if len(chunk) >= min_chunk_size:
            chunks_with_meta.append({
                "text": chunk,
                "metadata": {
                    "article_ref": f"Đoạn {len(chunks_with_meta) + 1}",
                    "parent_context": "",
                }
            })
        start += chunk_size - overlap

    print(f"[RAG] Sliding window: {len(chunks_with_meta)} chunks ({chunk_size} chars, {overlap} overlap)")
    return chunks_with_meta


# ──────────────────────────────────────────────
# 6. INGEST: DOCUMENT → ChromaDB
# ──────────────────────────────────────────────
def ingest_document(file_path: str, source_name: Optional[str] = None, force: bool = False) -> dict:
    """
    Đọc tài liệu, validate chất lượng, chunking và lưu vào ChromaDB.
    
    Args:
        file_path: Đường dẫn tới file PDF/DOCX
        source_name: Tên nguồn (mặc định = tên file)
        force: Nếu True, bỏ qua validation (vẫn ingest cả tài liệu LOW quality)
    
    Returns:
        dict: {
            "num_chunks": int,
            "validation": {...},   # Kết quả validation
            "forced": bool,        # True nếu bị force qua validation
        }
    """
    from document_validator import validate_legal_document, format_validation_report

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    source_name = source_name or os.path.basename(file_path)
    raw_text = read_document(file_path)
    
    # ── VALIDATION STEP ──
    validation = validate_legal_document(raw_text)
    quality = validation["quality"]
    score = validation["score"]
    
    print(format_validation_report(validation))
    
    if quality == "LOW" and not force:
        raise ValueError(
            f"Tài liệu không đạt chất lượng (score={score}/100, quality={quality}). "
            f"Lý do: {validation['summary']}. "
            f"Sử dụng --force để bỏ qua kiểm tra."
        )
    
    if quality == "MEDIUM":
        print(f"[RAG] ⚠️ CẢNH BÁO: Tài liệu chất lượng TRUNG BÌNH (score={score}/100).")
        print(f"[RAG]    {validation['summary']}")
        print(f"[RAG]    Tiếp tục ingest nhưng kết quả có thể không chính xác.")
    
    # ── CHUNKING (hierarchical) ──
    chunk_dicts = chunk_legal_text(raw_text)
    
    # Tách lấy danh sách text để đưa vào mô hình Embedding
    texts_to_embed = [c["text"] for c in chunk_dicts]

    print(f"[RAG] Đang embedding {len(texts_to_embed)} chunks …")
    embeddings = embed_texts(texts_to_embed)

    collection = get_collection()

    ids = [str(uuid.uuid4()) for _ in texts_to_embed]
    
    # Nạp thêm metadata article_ref + quality vào ChromaDB
    metadatas = []
    for i, c in enumerate(chunk_dicts):
        meta = {
            "source": source_name, 
            "chunk_index": i,
            "article_ref": c["metadata"]["article_ref"],  # Dữ liệu quan trọng để so sánh
            "parent_context": c["metadata"].get("parent_context", ""),
            "doc_quality": quality,                         # Chất lượng tài liệu
            "doc_quality_score": score,                     # Điểm chất lượng
        }
        metadatas.append(meta)

    batch_size = 100
    for i in range(0, len(texts_to_embed), batch_size):
        collection.upsert(
            ids=ids[i : i + batch_size],
            documents=texts_to_embed[i : i + batch_size],
            embeddings=embeddings[i : i + batch_size],
            metadatas=metadatas[i : i + batch_size],
        )

    print(f"[RAG] ✅ Đã lưu {len(texts_to_embed)} chunks từ '{source_name}' vào ChromaDB.")
    return {
        "num_chunks": len(texts_to_embed),
        "validation": validation,
        "forced": quality == "LOW" and force,
    }

# ──────────────────────────────────────────────
# 7. SOURCE DETECTION FROM QUERY
# ──────────────────────────────────────────────

# Mapping keywords trong câu hỏi → source name
_SOURCE_KEYWORDS = {
    "ThueNha_V1": [
        r"thuê\s*nhà\s*v1", r"thuê\s*nhà\s*(?:phiên\s*bản\s*)?1",
        r"hợp\s*đồng\s*thuê\s*nhà\s*v1",
        r"thue\s*nha\s*v1",
    ],
    "ThueNha_V2": [
        r"thuê\s*nhà\s*v2", r"thuê\s*nhà\s*(?:phiên\s*bản\s*)?2",
        r"hợp\s*đồng\s*thuê\s*nhà\s*v2",
        r"thue\s*nha\s*v2",
    ],
    "DichVu_BaoTri": [
        r"bảo\s*trì", r"dịch\s*vụ\s*bảo\s*trì", r"sla", r"uptime",
        r"bao\s*tri", r"dich\s*vu\s*bao\s*tri",
    ],
    "LaoDong": [
        r"lao\s*động", r"nhân\s*viên", r"lương", r"thử\s*việc",
        r"phụ\s*cấp", r"nghỉ\s*phép", r"giờ\s*làm",
        r"lao\s*dong", r"nhan\s*vien", r"luong", r"thu\s*viec",
        r"phu\s*cap", r"nghi\s*phep", r"gio\s*lam",
    ],
    "MuaBan_ThietBi": [
        r"thiết\s*bị", r"mua\s*bán", r"bảo\s*hành",
        r"thiet\s*bi", r"mua\s*ban", r"bao\s*hanh",
    ],
    "HopDong_V1": [
        r"hợp\s*đồng\s*v1", r"hợp\s*đồng\s*(?:gốc\s*)?(?:phiên\s*bản\s*)?1",
        r"hop\s*dong\s*v1",
    ],
    "HopDong_V2": [
        r"hợp\s*đồng\s*v2", r"hợp\s*đồng\s*(?:gốc\s*)?(?:phiên\s*bản\s*)?2",
        r"hop\s*dong\s*v2",
    ],
    "PhuLuc_V1": [
        r"phụ\s*lục\s*(?:kho\s*)?v1",
        r"phu\s*luc\s*(?:kho\s*)?v1",
    ],
    "PhuLuc_V2": [
        r"phụ\s*lục\s*(?:kho\s*)?v2",
        r"phu\s*luc\s*(?:kho\s*)?v2",
    ],
}



# Patterns cho câu hỏi tổng hợp / cross-document → KHÔNG nên lock vào 1 source
_CROSS_DOC_PATTERNS = [
    r"(?:hợp\s*đồng|tài\s*liệu)\s*nào",
    r"so\s*sánh.*(?:giữa|các|hợp\s*đồng)",
    r"các\s*hợp\s*đồng",
    r"tất\s*cả",
    r"lớn\s*nhất",
    r"nhỏ\s*nhất",
    r"dài\s*nhất",
    r"ngắn\s*nhất",
    r"liệt\s*kê.*hợp\s*đồng",
]


def _is_cross_doc_query(query: str) -> bool:
    """Kiểm tra câu hỏi có yêu cầu dữ liệu từ nhiều nguồn không."""
    query_lower = query.lower()
    for pattern in _CROSS_DOC_PATTERNS:
        if re.search(pattern, query_lower):
            return True
    return False


def detect_source_from_query(query: str) -> Optional[str]:
    """
    Tự động detect source name từ câu hỏi.
    VD: "Giá thuê nhà V1 là bao nhiêu?" → "ThueNha_V1"
    VD: "SLA của hợp đồng bảo trì?" → "DichVu_BaoTri"
    
    Returns None nếu không detect được (sẽ search tất cả sources).
    
    Week 11 improvement: Tự động trả None cho câu hỏi cross-document
    để tránh lock vào 1 source duy nhất.
    """
    query_lower = query.lower()
    
    # Cross-document query → KHÔNG filter source, tìm tất cả
    if _is_cross_doc_query(query):
        print(f"[RAG] Cross-document query detected → search tất cả sources")
        return None
    
    # Ưu tiên match cụ thể (có version) trước match chung
    # Sắp xếp: source có "V1/V2" trước, source chung sau
    specific_sources = {k: v for k, v in _SOURCE_KEYWORDS.items() if k.endswith(("_V1", "_V2"))}
    general_sources = {k: v for k, v in _SOURCE_KEYWORDS.items() if not k.endswith(("_V1", "_V2"))}
    
    # Check specific first
    for source, patterns in specific_sources.items():
        for pattern in patterns:
            if re.search(pattern, query_lower):
                return source
    
    # Then general
    for source, patterns in general_sources.items():
        for pattern in patterns:
            if re.search(pattern, query_lower):
                return source
    
    return None


_OVERLAP_STOPWORDS: Set[str] = {
    "cua", "cho", "la", "nhung", "trong", "voi", "duoc", "the", "nao",
    "bao", "nhieu", "gi", "ve", "cac", "hop", "dong", "tai", "lieu",
    "theo", "mot", "cac", "toi", "den", "khi", "neu", "thi", "day",
}


def _tokenize_for_overlap(text: str) -> Set[str]:
    """Tokenize đơn giản để tính lexical overlap cho rerank."""
    tokens = re.findall(r"[a-zA-Z0-9_À-ỹ]+", text.lower())
    return {t for t in tokens if len(t) > 2 and t not in _OVERLAP_STOPWORDS}


def _lexical_overlap_score(query: str, text: str) -> float:
    """Điểm overlap giữa token query và chunk text, từ 0.0 -> 1.0."""
    query_tokens = _tokenize_for_overlap(query)
    if not query_tokens:
        return 0.0
    text_tokens = _tokenize_for_overlap(text)
    if not text_tokens:
        return 0.0
    return len(query_tokens.intersection(text_tokens)) / len(query_tokens)


def _rerank_and_diversify_hits(query: str, hits: List[dict], top_k: int, is_cross_doc: bool) -> List[dict]:
    """
    Hybrid rerank (dense + lexical overlap) và đa dạng nguồn cho câu hỏi cross-document. Ghép giữa ngữ nghĩa và từ khoá để truy xuất chính xác điều cần tìm.
    """
    query_lower = query.lower()
    expects_money = any(k in query_lower for k in ["giá", "giá trị", "bao nhiêu", "chi phí", "lương", "cọc"])
    expects_payment = "thanh toán" in query_lower
    expects_duration = any(k in query_lower for k in ["thời hạn", "bao lâu", "tháng", "năm"])

    ranked = []
    for hit in hits:
        hit_text = hit.get("text", "")
        hit_text_lower = hit_text.lower()

        dense_score = max(0.0, 1.0 - float(hit.get("distance", 1.0)))
        lexical_score = _lexical_overlap_score(query, hit_text)

        intent_bonus = 0.0
        if expects_money and re.search(r"\d{1,3}(?:[\.,]\d{3})+", hit_text):
            intent_bonus += 0.08
        if expects_payment and re.search(r"thanh toán|chuyển khoản|đợt", hit_text_lower):
            intent_bonus += 0.08
        if expects_duration and re.search(r"thời hạn|tháng|năm", hit_text_lower):
            intent_bonus += 0.05

        final_score = (0.75 * dense_score) + (0.25 * lexical_score) + intent_bonus
        ranked.append({"score": final_score, "hit": hit})

    ranked.sort(key=lambda x: x["score"], reverse=True)

    selected = []
    selected_keys = set()
    source_counts = defaultdict(int)
    max_per_source = CROSS_DOC_MAX_PER_SOURCE if is_cross_doc else top_k

    for item in ranked:
        hit = item["hit"]
        meta = hit.get("metadata", {})
        source = meta.get("source", "Unknown")
        chunk_idx = meta.get("chunk_index", -1)
        key = (source, chunk_idx)

        if key in selected_keys:
            continue
        if source_counts[source] >= max_per_source:
            continue

        selected.append(hit)
        selected_keys.add(key)
        source_counts[source] += 1

        if len(selected) >= top_k:
            break

    # Nếu chưa đủ top_k thì nới giới hạn source để lấp đầy kết quả.
    if len(selected) < top_k:
        for item in ranked:
            hit = item["hit"]
            meta = hit.get("metadata", {})
            source = meta.get("source", "Unknown")
            chunk_idx = meta.get("chunk_index", -1)
            key = (source, chunk_idx)

            if key in selected_keys:
                continue

            selected.append(hit)
            selected_keys.add(key)
            if len(selected) >= top_k:
                break

    return selected[:top_k]


# ──────────────────────────────────────────────
# 8. RETRIEVAL
# ──────────────────────────────────────────────
def retrieve(query: str, top_k: int = DEFAULT_TOP_K, source_filter: Optional[str] = None, 
             auto_detect_source: bool = True, distance_threshold: float = DISTANCE_THRESHOLD) -> List[dict]:
    """
    Embed the query and return top_k most relevant chunks from ChromaDB.
    
    Week 11 improvements:
    - source_filter: chỉ lấy chunks từ source cụ thể
    - auto_detect_source: tự động detect source từ câu hỏi
    - distance_threshold: loại bỏ chunks quá xa (noise)
    - Dynamic top_k: tăng K cho cross-document queries
    """
    # Auto-detect source từ query nếu chưa được chỉ định
    is_cross_doc = False
    if source_filter is None and auto_detect_source:
        source_filter = detect_source_from_query(query)
        if source_filter:
            print(f"[RAG] Auto-detected source: {source_filter}")
        else:
            is_cross_doc = _is_cross_doc_query(query)
    
    # Dynamic top_k: tăng K cho cross-document queries để bao phủ nhiều source
    effective_top_k = CROSS_DOC_TOP_K if (is_cross_doc and source_filter is None) else top_k
    if effective_top_k != top_k:
        print(f"[RAG] Cross-doc mode: top_k {top_k} → {effective_top_k}")

    # Query nhiều candidates hơn để rerank/diversify ở bước sau.
    if is_cross_doc and source_filter is None:
        candidate_k = max(effective_top_k * RETRIEVAL_CANDIDATE_MULTIPLIER, 20)
    else:
        candidate_k = max(effective_top_k * 2, effective_top_k)
    
    query_embedding = embed_texts([query])[0]
    collection = get_collection()

    # Build query params
    query_params = {
        "query_embeddings": [query_embedding],
        "n_results": candidate_k,
        "include": ["documents", "metadatas", "distances"],
    }
    
    # Add source filter if specified
    if source_filter:
        normalized_source = normalize_source_name(source_filter)

        # Source không tồn tại -> trả về rỗng để tránh trả lời nhầm nguồn.
        available_sources = list_available_sources()
        if normalized_source not in available_sources:
            print(f"[RAG] ⚠️ Source '{source_filter}' không tồn tại trong DB (normalized='{normalized_source}').")
            return []

        query_params["where"] = {"source": normalized_source}

    try:
        results = collection.query(**query_params)
    except Exception as e:
        # Source filter lỗi thì trả rỗng để giữ nguyên tắc không trả lời sai nguồn.
        if source_filter:
            print(f"[RAG] ⚠️ Source filter '{source_filter}' thất bại: {e}")
            return []
        else:
            raise

    effective_threshold = distance_threshold
    if is_cross_doc and source_filter is None:
        # Cross-document dễ nhiễu hơn, dùng threshold chặt hơn.
        effective_threshold = min(distance_threshold, 0.9)

    hits = []
    if results["documents"] and results["documents"][0]:
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            # Distance threshold: loại bỏ chunks quá xa
            if dist > effective_threshold:
                continue
            hits.append({"text": doc, "metadata": meta, "distance": dist})

    if not hits:
        return []

    return _rerank_and_diversify_hits(
        query=query,
        hits=hits,
        top_k=effective_top_k,
        is_cross_doc=is_cross_doc,
    )

def retrieve_article_pair(article_name: str, source_v1: str = "HopDong_V1", source_v2: str = "HopDong_V2") -> dict:
    """
    Sử dụng Metadata Filtering để rút chính xác một Điều khoản từ 2 phiên bản ra so sánh.
    
    Week 11: Thêm fuzzy matching cho source name + article name.
    """
    collection = get_collection()
    
    # Normalize source names qua alias table
    norm_v1 = normalize_source_name(source_v1)
    norm_v2 = normalize_source_name(source_v2)
    
    # Normalize article name: "Điều 3" → chấp nhận cả "Điều 3", "Điều 3.", "Điều 3:"
    norm_article = article_name.strip()
    
    # 1. Lọc lấy văn bản của V1
    try:
        results_v1 = collection.get(
            where={
                "$and": [
                    {"source": norm_v1},
                    {"article_ref": norm_article}
                ]
            }
        )
    except Exception:
        results_v1 = {"documents": []}
    
    # Fallback: thử title case nếu không tìm thấy
    if not results_v1["documents"]:
        norm_article_title = norm_article.title()
        try:
            results_v1 = collection.get(
                where={
                    "$and": [
                        {"source": norm_v1},
                        {"article_ref": norm_article_title}
                    ]
                }
            )
        except Exception:
            results_v1 = {"documents": []}
    
    # 2. Lọc lấy văn bản của V2
    try:
        results_v2 = collection.get(
            where={
                "$and": [
                    {"source": norm_v2},
                    {"article_ref": norm_article}
                ]
            }
        )
    except Exception:
        results_v2 = {"documents": []}
    
    if not results_v2["documents"]:
        norm_article_title = norm_article.title()
        try:
            results_v2 = collection.get(
                where={
                    "$and": [
                        {"source": norm_v2},
                        {"article_ref": norm_article_title}
                    ]
                }
            )
        except Exception:
            results_v2 = {"documents": []}
    
    # 3. Trích xuất nội dung text
    if results_v1["documents"]:
        text_v1 = "\n\n".join(results_v1["documents"]) if len(results_v1["documents"]) > 1 else results_v1["documents"][0]
    else:
        text_v1 = f"Không tìm thấy {norm_article} trong nguồn {norm_v1}."
        # Debug: list available articles for this source
        try:
            all_v1 = collection.get(where={"source": norm_v1})
            available = set(m.get("article_ref", "?") for m in all_v1["metadatas"])
            if available:
                text_v1 += f" (Các điều có sẵn: {', '.join(sorted(available))})"
        except Exception:
            pass
    
    if results_v2["documents"]:
        text_v2 = "\n\n".join(results_v2["documents"]) if len(results_v2["documents"]) > 1 else results_v2["documents"][0]
    else:
        text_v2 = f"Không tìm thấy {norm_article} trong nguồn {norm_v2}."
        try:
            all_v2 = collection.get(where={"source": norm_v2})
            available = set(m.get("article_ref", "?") for m in all_v2["metadatas"])
            if available:
                text_v2 += f" (Các điều có sẵn: {', '.join(sorted(available))})"
        except Exception:
            pass
    
    return {
        "article_name": article_name,
        "v1_text": text_v1,
        "v2_text": text_v2
    }

def generate_comparison_report(article_name: str, source_v1: str, source_v2: str, model: str = QWEN_MODEL) -> dict:
    """
    Sinh báo cáo so sánh 2 phiên bản của cùng một điều khoản.
    Tuân thủ nguyên tắc: "Không bằng chứng → Không kết luận"

    Week 12: Cải tiến compare pipeline
      - Đảo thứ tự prompt: KHÁC BIỆT viết trước, TÓM TẮT sau
      - Tăng num_predict 2048 → 4096
      - Thêm truncation detection
      - Yêu cầu liệt kê cả thay đổi nhỏ

    Returns:
        dict with keys: article_name, v1_text, v2_text, comparison_report, model, citations
    """
    import requests

    # Lấy nội dung 2 phiên bản
    data = retrieve_article_pair(article_name, source_v1, source_v2)

    v1_text = data['v1_text']
    v2_text = data['v2_text']

    # Kiểm tra xem có đủ dữ liệu không
    if "Không tìm thấy" in v1_text and "Không tìm thấy" in v2_text:
        return {
            "article_name": article_name,
            "v1_text": v1_text,
            "v2_text": v2_text,
            "comparison_report": "Không tìm thấy điều khoản này trong cả hai phiên bản tài liệu.",
            "model": model,
            "citations": []
        }

    # Xây dựng prompt so sánh (Week 12 — ưu tiên KHÁC BIỆT trước)
    prompt = f"""Bạn là trợ lý AI phân tích tài liệu pháp lý. Nhiệm vụ: SO SÁNH hai phiên bản của "{article_name}".

NGUYÊN TẮC BẮT BUỘC:
1. CHỈ dựa vào nội dung được cung cấp bên dưới. KHÔNG suy luận hay thêm thắt.
2. TRÍCH DẪN trực tiếp câu/cụm từ từ văn bản gốc (dùng dấu "..." để quote).
3. Nếu không tìm thấy khác biệt → nói rõ "Không phát hiện sự khác biệt".
4. Nếu thiếu thông tin → nói rõ "Không đủ thông tin để kết luận".
5. Kể cả thay đổi NHỎ (thêm/bớt 1-2 từ, thay đổi con số) cũng phải liệt kê trong ĐIỂM KHÁC BIỆT.

=== PHIÊN BẢN 1: {source_v1} ===
{v1_text}

=== PHIÊN BẢN 2: {source_v2} ===
{v2_text}

=== YÊU CẦU ===
Tạo báo cáo ĐÚNG THỨ TỰ sau (viết KHÁC BIỆT trước, TÓM TẮT sau):

**1. ĐIỂM KHÁC BIỆT**
- ĐÂY LÀ PHẦN QUAN TRỌNG NHẤT. Viết đầy đủ, không được bỏ sót.
- Liệt kê TỪNG điểm khác biệt theo format:
  * [Trường/Khoản]: V1 = "quote V1" → V2 = "quote V2"
- So sánh từng khoản tương ứng giữa V1 và V2. Nếu con số, ngày tháng, hoặc từ ngữ khác nhau → liệt kê.
- Nếu không có khác biệt: "Không phát hiện sự khác biệt"

**2. NỘI DUNG MỚI THÊM/BỎ ĐI**
- V2 thêm mới (không có trong V1): liệt kê
- V1 có nhưng V2 bỏ: liệt kê
- Nếu không có: "Không phát hiện nội dung mới/bỏ đi"

**3. ĐIỂM GIỐNG NHAU**
- Liệt kê ngắn gọn các điểm giống nhau. Nếu không có: "Không phát hiện điểm giống nhau rõ ràng"

**4. TÓM TẮT V1 ({source_v1})**
- Liệt kê ngắn gọn các nội dung chính.

**5. TÓM TẮT V2 ({source_v2})**
- Liệt kê ngắn gọn các nội dung chính.

=== BÁO CÁO SO SÁNH ==="""

    # Gọi LLM
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 4096},  # Token budget đủ cho báo cáo 5 phần
    }

    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=300)
        response.raise_for_status()
        comparison_report = response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        comparison_report = (
            f"[Lỗi] Không thể kết nối tới Ollama. "
            f"Hãy chắc chắn Ollama đang chạy và model {model} đã được tải."
        )
    except Exception as e:
        comparison_report = f"[Lỗi] {str(e)}"

    # Truncation detection: cảnh báo nếu output bị cắt giữa chừng
    if comparison_report and not comparison_report.startswith("[Lỗi]"):
        has_diff_section = "ĐIỂM KHÁC BIỆT" in comparison_report or "KHÁC BIỆT" in comparison_report
        if not has_diff_section:
            comparison_report += "\n\n⚠️ Báo cáo có thể bị cắt ngắn — không tìm thấy phần ĐIỂM KHÁC BIỆT. Vui lòng thử lại."

    # Tạo citations
    citations = []
    if "Không tìm thấy" not in v1_text:
        citations.append({
            "source": source_v1,
            "article_ref": article_name,
            "excerpt": v1_text[:200] + "..." if len(v1_text) > 200 else v1_text
        })
    if "Không tìm thấy" not in v2_text:
        citations.append({
            "source": source_v2,
            "article_ref": article_name,
            "excerpt": v2_text[:200] + "..." if len(v2_text) > 200 else v2_text
        })

    return {
        "article_name": article_name,
        "v1_text": v1_text,
        "v2_text": v2_text,
        "comparison_report": comparison_report,
        "model": model,
        "citations": citations
    }

# ──────────────────────────────────────────────
# 9. LLM ANSWER GENERATION via Ollama
# ──────────────────────────────────────────────
def build_prompt(question: str, context_chunks: List[dict]) -> str:
    """
    Build prompt with metadata for citation.
    
    Week 11 v2: Balanced prompt — giảm over-refusal, giữ anti-hallucination.
    Thay đổi chính:
    - Giảm cụm "TUYỆT ĐỐI" → model linh hoạt hơn khi context có dữ liệu
    - Thêm ví dụ ĐÚNG cho trường hợp nhiều source
    - Phân biệt rõ "hoàn toàn không có" vs "có nhưng không đầy đủ"
    """
    context_parts = []
    for i, c in enumerate(context_chunks):
        source = c['metadata'].get('source', 'Unknown')
        article = c['metadata'].get('article_ref', 'Unknown')
        context_parts.append(
            f"[Chunk {i+1} — Nguồn: {source}, {article}]\n{c['text']}"
        )
    context_text = "\n\n---\n\n".join(context_parts)

    prompt = f"""Bạn là trợ lý AI phân tích tài liệu pháp lý. Tuân thủ các nguyên tắc sau:

NGUYÊN TẮC:
1. Trả lời DỰA TRÊN ngữ cảnh bên dưới. Không dùng kiến thức bên ngoài.
2. TRÍCH DẪN nguồn sau mỗi thông tin: [Nguồn: <tên>, <điều>]
3. Nếu ngữ cảnh HOÀN TOÀN không liên quan đến câu hỏi → trả lời: "Không tìm thấy thông tin trong tài liệu được cung cấp."
4. Nếu ngữ cảnh có thông tin liên quan nhưng CHƯA ĐẦY ĐỦ → trả lời phần có thông tin, ghi chú phần còn thiếu.
5. Nếu ngữ cảnh có dữ liệu từ NHIỀU nguồn → liệt kê thông tin từ từng nguồn, nêu rõ sự khác biệt.
6. Nếu câu hỏi hỏi về nguồn CỤ THỂ (VD: "thuê nhà V1") nhưng ngữ cảnh chỉ có nguồn KHÁC → nói rõ không tìm thấy trong nguồn đó.

VÍ DỤ 1 (không có thông tin → từ chối):
Câu hỏi: "Thuế VAT trong hợp đồng thuê nhà là bao nhiêu?"
Ngữ cảnh: [chỉ có thông tin VAT từ hợp đồng mua bán thiết bị]
→ "Không tìm thấy thông tin về thuế VAT trong hợp đồng thuê nhà."

VÍ DỤ 2 (có thông tin từ nhiều nguồn → trả lời đầy đủ):
Câu hỏi: "Giá thuê nhà là bao nhiêu?"
Ngữ cảnh: [Điều 3 V1: 5.000.000 VNĐ/tháng] [Điều 3 V2: 6.000.000 VNĐ/tháng]
→ "Theo Điều 3:
- ThueNha_V1: Giá thuê là 5.000.000 VNĐ/tháng [Nguồn: ThueNha_V1, Điều 3]
- ThueNha_V2: Giá thuê là 6.000.000 VNĐ/tháng [Nguồn: ThueNha_V2, Điều 3]"

VÍ DỤ 3 (có thông tin nhưng chưa đầy đủ → trả lời phần có):
Câu hỏi: "Lương và phụ cấp của nhân viên?"
Ngữ cảnh: [Điều 5: Lương 15.000.000 VNĐ/tháng, nhưng không đề cập phụ cấp]
→ "Lương cơ bản là 15.000.000 VNĐ/tháng [Nguồn: LaoDong, Điều 5]. Thông tin về phụ cấp không được đề cập trong ngữ cảnh được cung cấp."

=== NGỮ CẢNH ===
{context_text}

=== CÂU HỎI ===
{question}

=== TRẢ LỜI (trích dẫn nguồn, trả lời đầy đủ thông tin CÓ trong ngữ cảnh) ==="""

    return prompt


def _postprocess_answer(answer: str, chunks: List[dict], question: str) -> str:
    """
    Post-processing: kiểm tra faithfulness cơ bản.
    
    Nếu phát hiện dấu hiệu hallucination → thêm disclaimer.
    """
    if not answer or not chunks:
        return answer
    
    # Kiểm tra: nếu answer chứa số liệu mà KHÔNG có trong bất kỳ chunk nào
    # (đơn giản: check số tiền lớn)
    money_pattern = r"\d{1,3}(?:\.\d{3})+"
    answer_numbers = set(re.findall(money_pattern, answer))
    
    all_chunk_text = " ".join(c["text"] for c in chunks)
    chunk_numbers = set(re.findall(money_pattern, all_chunk_text))
    
    # Số liệu trong answer nhưng không trong chunks = có thể bịa
    suspicious_numbers = answer_numbers - chunk_numbers
    
    if suspicious_numbers and len(suspicious_numbers) > 1:
        answer += "\n\n⚠️ Lưu ý: Một số thông tin có thể không chính xác. Vui lòng kiểm tra lại với tài liệu gốc."
    
    return answer


def ask_ollama(
    question: str,
    model: str = QWEN_MODEL,
    top_k: int = DEFAULT_TOP_K,
    source_filter: Optional[str] = None,
    auto_detect_source: bool = True,
) -> dict:
    """
    Full RAG pipeline:
      1. Retrieve top_k relevant chunks from ChromaDB (source-aware)
      2. Build prompt (few-shot anti-hallucination)
      3. Call Ollama LLM
      4. Post-process answer
    Returns dict with keys: answer, model, chunks_used, citations
    """
    import requests

    hits = retrieve(
        query=question,
        top_k=top_k,
        source_filter=source_filter,
        auto_detect_source=auto_detect_source,
    )
    if not hits:
        return {
            "answer": "Không tìm thấy thông tin liên quan trong cơ sở dữ liệu.",
            "model": model,
            "chunks_used": [],
            "citations": []
        }

    prompt = build_prompt(question, hits)

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 768},  # temp 0.2→0.3, tokens 512→768 cho trả lời đầy đủ hơn
    }

    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
        response.raise_for_status()
        answer = response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        answer = (
            "[Lỗi] Không thể kết nối tới Ollama. "
            "Hãy chắc chắn Ollama đang chạy: `ollama serve` "
            f"và model đã được tải: `ollama pull {model}`"
        )
    except Exception as e:
        answer = f"[Lỗi] {str(e)}"

    # Post-process: faithfulness check
    answer = _postprocess_answer(answer, hits, question)

    # Extract citations from chunks used
    citations = []
    for chunk in hits:
        citations.append({
            "source": chunk['metadata'].get('source', 'Unknown'),
            "article_ref": chunk['metadata'].get('article_ref', 'Unknown'),
            "excerpt": chunk['text'][:150] + "..." if len(chunk['text']) > 150 else chunk['text']
        })

    return {
        "answer": answer,
        "model": model,
        "chunks_used": hits,
        "citations": citations
    }


async def ask_ollama_async(
    question: str,
    model: str = QWEN_MODEL,
    top_k: int = DEFAULT_TOP_K,
    source_filter: Optional[str] = None,
    auto_detect_source: bool = True,
) -> dict:
    """Async wrapper for use with discord bot."""
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: ask_ollama(
            question=question,
            model=model,
            top_k=top_k,
            source_filter=source_filter,
            auto_detect_source=auto_detect_source,
        ),
    )

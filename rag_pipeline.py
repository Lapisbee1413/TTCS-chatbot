"""
RAG Pipeline – PDF → Chunking → ChromaDB → Q&A
Models  : Qwen 2.5 (3B) and/or Mistral 7B via Ollama (local)
Embeddings: sentence-transformers (local)
"""

import os
import re
import uuid
from typing import List, Optional
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
QWEN_MODEL    = "qwen2.5:1.5b"
MISTRAL_MODEL = "mistral"

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
# 5. CHUNKING (Pattern-based Chunking cho Luật)
# ──────────────────────────────────────────────
def chunk_legal_text(text: str, min_chunk_size: int = 50) -> List[dict]:
    """
    Chia đoạn dựa trên cấu trúc "Điều X".
    Trả về danh sách dictionary gồm đoạn text và metadata (số Điều).

    Args:
        text: Văn bản cần chia
        min_chunk_size: Kích thước tối thiểu của chunk (chars). Chunks nhỏ hơn sẽ bị loại bỏ.
    """
    # Chuẩn hóa khoảng trắng
    text = re.sub(r"\n{3,}", "\n\n", text.strip())

    # Biểu thức chính quy (Regex) tìm điểm chia: Bắt đầu bằng chữ "Điều" + Số
    # Phép (?=...) giúp cắt mà không làm mất đi chữ "Điều" ở đầu chunk
    pattern = r"(?i)(?=\bĐiều\s+\d+[\.\:])"

    raw_chunks = re.split(pattern, text)
    chunks_with_meta = []

    for chunk in raw_chunks:
        chunk = chunk.strip()

        # Bỏ qua chunks quá ngắn (thường là lỗi format hoặc không có nội dung thật)
        if len(chunk) < min_chunk_size:
            continue

        # Tìm xem chunk này thuộc Điều mấy để gắn vào metadata
        match = re.match(r"(?i)(Điều\s+\d+)", chunk)
        article_ref = match.group(1).title() if match else "Thông tin chung"

        chunks_with_meta.append({
            "text": chunk,
            "metadata": {"article_ref": article_ref}
        })

    # Cảnh báo nếu không có chunk nào sau khi filter
    if not chunks_with_meta:
        print(f"[RAG] [WARNING] Không tìm thấy chunk hợp lệ nào (min_size={min_chunk_size}). Đang giữ lại toàn bộ văn bản.")
        chunks_with_meta.append({
            "text": text,
            "metadata": {"article_ref": "Toàn bộ tài liệu"}
        })

    print(f"[RAG] Đã tạo {len(chunks_with_meta)} chunks theo cấu trúc Điều khoản (đã lọc chunks < {min_chunk_size} chars).")
    return chunks_with_meta

# ──────────────────────────────────────────────
# 6. INGEST: DOCUMENT → ChromaDB
# ──────────────────────────────────────────────
def ingest_document(file_path: str, source_name: Optional[str] = None) -> int:
    """
    Cập nhật hàm ingest để dùng hàm đọc và chunking mới.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    source_name = source_name or os.path.basename(file_path)
    raw_text = read_document(file_path)
    
    # Gọi hàm chunking mới
    chunk_dicts = chunk_legal_text(raw_text)
    
    # Tách lấy danh sách text để đưa vào mô hình Embedding
    texts_to_embed = [c["text"] for c in chunk_dicts]

    print(f"[RAG] Đang embedding {len(texts_to_embed)} chunks …")
    embeddings = embed_texts(texts_to_embed)

    collection = get_collection()

    ids = [str(uuid.uuid4()) for _ in texts_to_embed]
    
    # Nạp thêm metadata article_ref vào ChromaDB
    metadatas = []
    for i, c in enumerate(chunk_dicts):
        meta = {
            "source": source_name, 
            "chunk_index": i,
            "article_ref": c["metadata"]["article_ref"] # Dữ liệu quan trọng để so sánh
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
    return len(texts_to_embed)

# ──────────────────────────────────────────────
# 7. RETRIEVAL
# ──────────────────────────────────────────────
def retrieve(query: str, top_k: int = 5) -> List[dict]:
    """
    Embed the query and return top_k most relevant chunks from ChromaDB.
    """
    query_embedding = embed_texts([query])[0]
    collection = get_collection()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({"text": doc, "metadata": meta, "distance": dist})
    return hits

def retrieve_article_pair(article_name: str, source_v1: str = "HopDong_V1", source_v2: str = "HopDong_V2") -> dict:
    """
    Sử dụng Metadata Filtering để rút chính xác một Điều khoản từ 2 phiên bản ra so sánh.
    """
    collection = get_collection()
    
    # 1. Lọc lấy văn bản của V1
    results_v1 = collection.get(
        where={
            "$and": [
                {"source": source_v1},
                {"article_ref": article_name}
            ]
        }
    )
    
    # 2. Lọc lấy văn bản của V2
    results_v2 = collection.get(
        where={
            "$and": [
                {"source": source_v2},
                {"article_ref": article_name}
            ]
        }
    )
    
    # 3. Trích xuất nội dung text (xử lý luôn trường hợp nếu 1 bản không có điều khoản đó)
    text_v1 = results_v1["documents"][0] if results_v1["documents"] else "Không tìm thấy điều khoản này."
    text_v2 = results_v2["documents"][0] if results_v2["documents"] else "Không tìm thấy điều khoản này."
    
    return {
        "article_name": article_name,
        "v1_text": text_v1,
        "v2_text": text_v2
    }

def generate_comparison_report(article_name: str, source_v1: str, source_v2: str, model: str = QWEN_MODEL) -> dict:
    """
    Sinh báo cáo so sánh 2 phiên bản của cùng một điều khoản.
    Tuân thủ nguyên tắc: "Không bằng chứng → Không kết luận"

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

    # Xây dựng prompt so sánh
    prompt = f"""Bạn là trợ lý AI phân tích tài liệu pháp lý. Nhiệm vụ của bạn là SO SÁNH hai phiên bản của cùng một điều khoản.

NGUYÊN TẮC BẮT BUỘC:
1. CHỈ dựa vào nội dung được cung cấp bên dưới
2. KHÔNG suy luận, đoán mò hay thêm thắt thông tin không có
3. TRÍCH DẪN nguồn rõ ràng cho mọi nhận xét
4. Nếu không tìm thấy sự khác biệt → nói rõ "Không phát hiện sự khác biệt"
5. Nếu thiếu thông tin → nói rõ "Không đủ thông tin để kết luận"

=== PHIÊN BẢN 1: {source_v1} ===
{v1_text}

=== PHIÊN BẢN 2: {source_v2} ===
{v2_text}

=== YÊU CẦU ===
Hãy tạo báo cáo so sánh theo cấu trúc sau:

**1. NỘI DUNG PHIÊN BẢN 1 ({source_v1})**
[Tóm tắt ngắn gọn nội dung chính]

**2. NỘI DUNG PHIÊN BẢN 2 ({source_v2})**
[Tóm tắt ngắn gọn nội dung chính]

**3. ĐIỂM GIỐNG NHAU**
[Liệt kê các điểm giống nhau. Nếu không có, ghi: "Không phát hiện điểm giống nhau rõ ràng"]

**4. ĐIỂM KHÁC BIỆT**
[Liệt kê các điểm khác biệt CỤ THỂ với trích dẫn. Nếu không có, ghi: "Không phát hiện sự khác biệt"]

**5. TÓM TẮT THAY ĐỔI**
[Tóm tắt tổng quan về thay đổi từ V1 sang V2]

Nhớ: Mọi nhận xét phải có căn cứ cụ thể từ văn bản.

=== BÁO CÁO SO SÁNH ==="""

    # Gọi LLM
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2, "num_predict": 1024},
    }

    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=180)
        response.raise_for_status()
        comparison_report = response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        comparison_report = (
            f"[Lỗi] Không thể kết nối tới Ollama. "
            f"Hãy chắc chắn Ollama đang chạy và model {model} đã được tải."
        )
    except Exception as e:
        comparison_report = f"[Lỗi] {str(e)}"

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
# 8. LLM ANSWER GENERATION via Ollama
# ──────────────────────────────────────────────
def build_prompt(question: str, context_chunks: List[dict]) -> str:
    """Build prompt with metadata for citation"""
    context_parts = []
    for i, c in enumerate(context_chunks):
        source = c['metadata'].get('source', 'Unknown')
        article = c['metadata'].get('article_ref', 'Unknown')
        context_parts.append(
            f"[Chunk {i+1} - Nguồn: {source}, {article}]\n{c['text']}"
        )
    context_text = "\n\n---\n\n".join(context_parts)

    prompt = (
        "Bạn là trợ lý AI phân tích tài liệu pháp lý. Hãy tuân thủ các nguyên tắc sau:\n\n"
        "NGUYÊN TẮC BẮT BUỘC:\n"
        "1. CHỈ trả lời dựa trên ngữ cảnh được cung cấp bên dưới\n"
        "2. KHÔNG sử dụng kiến thức bên ngoài hoặc suy luận không có căn cứ\n"
        "3. Sau mỗi thông tin, PHẢI trích dẫn nguồn theo format: [Nguồn: <tên_nguồn>, <điều_khoản>]\n"
        "4. Nếu không tìm thấy thông tin trong ngữ cảnh → nói rõ 'Không tìm thấy thông tin trong tài liệu được cung cấp'\n"
        "5. Không đoán mò, diễn giải hay bổ sung thông tin không có trong ngữ cảnh\n\n"
        f"=== NGỮ CẢNH ===\n{context_text}\n\n"
        f"=== CÂU HỎI ===\n{question}\n\n"
        "=== TRẢ LỜI (nhớ trích dẫn nguồn sau mỗi thông tin) ==="
    )
    return prompt


def ask_ollama(question: str, model: str = QWEN_MODEL, top_k: int = 5) -> dict:
    """
    Full RAG pipeline:
      1. Retrieve top_k relevant chunks from ChromaDB
      2. Build prompt
      3. Call Ollama LLM
    Returns dict with keys: answer, model, chunks_used, citations
    """
    import requests

    hits = retrieve(question, top_k=top_k)
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
        "options": {"temperature": 0.3, "num_predict": 512},
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


async def ask_ollama_async(question: str, model: str = QWEN_MODEL, top_k: int = 5) -> dict:
    """Async wrapper for use with discord bot."""
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: ask_ollama(question, model, top_k))


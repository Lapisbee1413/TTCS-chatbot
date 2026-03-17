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
QWEN_MODEL    = "qwen2.5:3b"
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
def chunk_legal_text(text: str) -> List[dict]:
    """
    Chia đoạn dựa trên cấu trúc "Điều X".
    Trả về danh sách dictionary gồm đoạn text và metadata (số Điều).
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
        if not chunk: 
            continue
            
        # Tìm xem chunk này thuộc Điều mấy để gắn vào metadata
        match = re.match(r"(?i)(Điều\s+\d+)", chunk)
        article_ref = match.group(1).title() if match else "Thông tin chung"
        
        chunks_with_meta.append({
            "text": chunk,
            "metadata": {"article_ref": article_ref}
        })
        
    print(f"[RAG] Đã tạo {len(chunks_with_meta)} chunks theo cấu trúc Điều khoản.")
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
# ──────────────────────────────────────────────    
# 8. LLM ANSWER GENERATION via Ollama
# ──────────────────────────────────────────────
def build_prompt(question: str, context_chunks: List[dict]) -> str:
    context_text = "\n\n---\n\n".join(
        [f"[Chunk {i+1}] {c['text']}" for i, c in enumerate(context_chunks)]
    )
    prompt = (
        "Bạn là trợ lý AI thông minh. Hãy trả lời câu hỏi dựa trên ngữ cảnh được cung cấp.\n"
        "Nếu ngữ cảnh không đủ thông tin, hãy nói rõ điều đó.\n\n"
        f"=== NGỮ CẢNH ===\n{context_text}\n\n"
        f"=== CÂU HỎI ===\n{question}\n\n"
        "=== TRẢ LỜI ==="
    )
    return prompt


def ask_ollama(question: str, model: str = QWEN_MODEL, top_k: int = 5) -> dict:
    """
    Full RAG pipeline:
      1. Retrieve top_k relevant chunks from ChromaDB
      2. Build prompt
      3. Call Ollama LLM
    Returns dict with keys: answer, model, chunks_used
    """
    import requests

    hits = retrieve(question, top_k=top_k)
    if not hits:
        return {"answer": "Không tìm thấy thông tin liên quan trong cơ sở dữ liệu.", "model": model, "chunks_used": []}

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

    return {"answer": answer, "model": model, "chunks_used": hits}

# test_chunk.py
import docx
import re

# 1. Hàm đọc DOCX (copy từ rag_pipeline)
def read_docx(docx_path: str) -> str:
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

# 2. Hàm Chunking theo Luật (copy từ rag_pipeline)
def chunk_legal_text(text: str) -> list:
    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    pattern = r"(?i)(?=\bĐiều\s+\d+[\.\:])"
    raw_chunks = re.split(pattern, text)
    
    chunks_with_meta = []
    for chunk in raw_chunks:
        chunk = chunk.strip()
        if not chunk: continue
            
        match = re.match(r"(?i)(Điều\s+\d+)", chunk)
        article_ref = match.group(1).title() if match else "Thông tin chung"
        
        chunks_with_meta.append({
            "text": chunk,
            "metadata": {"article_ref": article_ref}
        })
    return chunks_with_meta

# 3. Chạy thử nghiệm
if __name__ == "__main__":
    print("--- ĐANG TEST FILE V1 ---")
    text_v1 = read_docx("hopdong_v1.docx")
    chunks_v1 = chunk_legal_text(text_v1)
    
    for i, chunk in enumerate(chunks_v1):
        print(f"\n[Chunk {i+1}] - Thuộc: {chunk['metadata']['article_ref']}")
        print(f"Nội dung: {chunk['text'][:100]}...") # Cắt ra 100 ký tự đầu
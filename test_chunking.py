"""
Test chunking để kiểm tra xem có bị mất dữ liệu không
"""
import re
from rag_pipeline import read_document, chunk_legal_text


def test_no_data_loss(file_path: str):
    """Kiểm tra xem chunking có làm mất dữ liệu không"""
    print(f"\n{'='*60}")
    print(f"TEST CHUNKING: {file_path}")
    print(f"{'='*60}\n")

    # Đọc file
    original_text = read_document(file_path)
    original_length = len(original_text)
    original_words = len(original_text.split())

    print(f"[*] Van ban goc:")
    print(f"   - Tong ky tu: {original_length:,}")
    print(f"   - Tong tu: {original_words:,}")
    print(f"   - Preview: {original_text[:200]}...")

    # Chunk
    chunks = chunk_legal_text(original_text)
    print(f"\n[*] Sau khi chunk:")
    print(f"   - So chunks: {len(chunks)}")

    # Tính tổng ký tự trong chunks
    total_chars_in_chunks = sum(len(c['text']) for c in chunks)
    total_words_in_chunks = sum(len(c['text'].split()) for c in chunks)

    print(f"   - Tong ky tu trong chunks: {total_chars_in_chunks:,}")
    print(f"   - Tong tu trong chunks: {total_words_in_chunks:,}")

    # Kiểm tra mất mát
    char_loss = original_length - total_chars_in_chunks
    word_loss = original_words - total_words_in_chunks

    char_loss_percent = (char_loss / original_length) * 100 if original_length > 0 else 0
    word_loss_percent = (word_loss / original_words) * 100 if original_words > 0 else 0

    print(f"\n[*] Danh gia:")
    print(f"   - Mat mat ky tu: {char_loss:,} ({char_loss_percent:.2f}%)")
    print(f"   - Mat mat tu: {word_loss:,} ({word_loss_percent:.2f}%)")

    # Cảnh báo nếu mất mát > 5%
    if char_loss_percent > 5 or word_loss_percent > 5:
        print(f"\n[!] CANH BAO: Co the bi mat du lieu dang ke!")
    else:
        print(f"\n[OK] Mat mat du lieu trong gioi han chap nhan duoc (do chuan hoa khoang trang)")

    # Hiển thị metadata các chunks
    print(f"\n[*] Danh sach chunks:")
    for i, chunk in enumerate(chunks):
        article_ref = chunk['metadata']['article_ref']
        text_preview = chunk['text'][:80].replace('\n', ' ')
        print(f"   {i+1:2d}. {article_ref:20s} | {len(chunk['text']):5,} chars | {text_preview}...")

    # Kiểm tra xem có chunk nào bất thường không (quá dài hoặc quá ngắn)
    print(f"\n[*] Kiem tra chunk bat thuong:")
    abnormal_found = False
    for i, chunk in enumerate(chunks):
        length = len(chunk['text'])
        if length < 50:  # Quá ngắn
            print(f"   [!] Chunk {i+1} qua ngan ({length} chars): {chunk['text'][:100]}")
            abnormal_found = True
        elif length > 5000:  # Quá dài
            print(f"   [!] Chunk {i+1} qua dai ({length} chars) - co the chua nhieu dieu khoan")
            abnormal_found = True

    if not abnormal_found:
        print(f"   [OK] Khong phat hien chunk bat thuong")

    print(f"\n{'='*60}\n")


def test_article_detection(file_path: str):
    """Kiểm tra xem có phát hiện đúng các điều khoản không"""
    print(f"\n{'='*60}")
    print(f"TEST PHAT HIEN DIEU KHOAN: {file_path}")
    print(f"{'='*60}\n")

    text = read_document(file_path)

    # Tìm tất cả "Điều X" trong văn bản gốc
    pattern = re.compile(r"(?i)\bĐiều\s+\d+", re.IGNORECASE)
    matches = pattern.findall(text)
    unique_articles = sorted(set([m.strip().title() for m in matches]))

    print(f"[*] Dieu khoan phat hien trong van ban goc:")
    print(f"   - Tong so lan xuat hien: {len(matches)}")
    print(f"   - So dieu khoan unique: {len(unique_articles)}")
    print(f"   - Danh sach: {', '.join(unique_articles)}")

    # Chunk và xem có phát hiện đủ không
    chunks = chunk_legal_text(text)
    chunk_articles = [c['metadata']['article_ref'] for c in chunks]
    unique_chunk_articles = sorted(set([a for a in chunk_articles if a != "Thông tin chung"]))

    print(f"\n[*] Dieu khoan trong chunks:")
    print(f"   - So chunks co dieu khoan: {len([a for a in chunk_articles if a != 'Thông tin chung'])}")
    print(f"   - So chunks 'Thong tin chung': {chunk_articles.count('Thông tin chung')}")
    print(f"   - So dieu khoan unique: {len(unique_chunk_articles)}")
    print(f"   - Danh sach: {', '.join(unique_chunk_articles)}")

    # So sánh
    missing = set(unique_articles) - set(unique_chunk_articles)
    extra = set(unique_chunk_articles) - set(unique_articles)

    if missing:
        print(f"\n[!] Thieu trong chunks: {', '.join(missing)}")
    if extra:
        print(f"\n[!] Thua trong chunks: {', '.join(extra)}")
    if not missing and not extra:
        print(f"\n[OK] Perfect match! Tat ca dieu khoan deu duoc phat hien chinh xac.")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    # Test với các file có sẵn
    test_files = [
        "hopdong_v1.docx",
        "hopdong_v2.docx",
        "phuluc_kho_v1.docx",
        "phuluc_kho_v2.docx"
    ]

    for file in test_files:
        try:
            test_no_data_loss(file)
            test_article_detection(file)
        except FileNotFoundError:
            print(f"[X] Khong tim thay file: {file}")
        except Exception as e:
            print(f"[X] Loi khi test {file}: {e}")

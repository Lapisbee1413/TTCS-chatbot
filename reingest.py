"""
Script để xóa dữ liệu cũ và re-ingest lại tất cả documents với chunking mới
"""
import os
import sys
import shutil

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from rag_pipeline import ingest_document, CHROMA_DB_PATH

def clean_and_reingest():
    """Xóa ChromaDB và ingest lại tất cả files"""

    # Danh sách files cần ingest
    files_to_ingest = [
        ("hopdong_v1.docx", "HopDong_V1"),
        ("hopdong_v2.docx", "HopDong_V2"),
        ("phuluc_kho_v1.docx", "PhuLuc_V1"),
        ("phuluc_kho_v2.docx", "PhuLuc_V2"),
    ]

    print("="*60)
    print("REINGEST SCRIPT - Xoa du lieu cu va ingest lai")
    print("="*60)

    # Bước 1: Xóa ChromaDB cũ
    if os.path.exists(CHROMA_DB_PATH):
        print(f"\n[1/3] Dang xoa ChromaDB cu tai: {CHROMA_DB_PATH}")
        try:
            shutil.rmtree(CHROMA_DB_PATH)
            print(f"      Da xoa thanh cong!")
        except Exception as e:
            print(f"      [!] Loi khi xoa: {e}")
            print(f"      Ban co the xoa thu cong folder: {CHROMA_DB_PATH}")
            return
    else:
        print(f"\n[1/3] Khong tim thay ChromaDB cu tai: {CHROMA_DB_PATH}")

    # Bước 2: Re-ingest từng file
    print(f"\n[2/3] Bat dau re-ingest {len(files_to_ingest)} files...")
    print("-"*60)

    success_count = 0
    for file_path, source_name in files_to_ingest:
        if not os.path.exists(file_path):
            print(f"[!] Khong tim thay file: {file_path} -> SKIP")
            continue

        try:
            print(f"\n[*] Ingesting: {file_path} -> source: {source_name}")
            num_chunks = ingest_document(file_path, source_name=source_name)
            print(f"    => OK: {num_chunks} chunks")
            success_count += 1
        except Exception as e:
            print(f"    => [X] LOI: {e}")

    # Bước 3: Kết quả
    print("\n" + "="*60)
    print(f"[3/3] KET QUA")
    print("="*60)
    print(f"  - Thanh cong: {success_count}/{len(files_to_ingest)} files")
    print(f"  - ChromaDB moi: {CHROMA_DB_PATH}")
    print("\nBan co the test bang:")
    print('  python query.py "Dieu 3 quy dinh gi?" --show-chunks')
    print("="*60 + "\n")


if __name__ == "__main__":
    clean_and_reingest()

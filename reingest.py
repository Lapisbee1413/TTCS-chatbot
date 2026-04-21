"""
Script để xóa dữ liệu cũ và re-ingest lại tất cả documents với chunking mới

Week 11: Đã thêm đủ tất cả tài liệu + source name khớp dataset evaluation
"""
import os
import sys
import shutil

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from rag_pipeline import ingest_document, CHROMA_DB_PATH, get_collection

def clean_and_reingest():
    """Xóa ChromaDB và ingest lại tất cả files"""

    # ── Danh sách đầy đủ files cần ingest ──
    # Source names PHẢI khớp với qa_dataset.json và compare_dataset.json
    test_docs_dir = os.path.join(os.path.dirname(__file__), "test_documents")

    files_to_ingest = [
        # Hợp đồng thuê nhà (so sánh V1 vs V2)
        (os.path.join(test_docs_dir, "hopdong_thue_nha_v1.docx"), "ThueNha_V1"),
        (os.path.join(test_docs_dir, "hopdong_thue_nha_v2.docx"), "ThueNha_V2"),
        # Hợp đồng gốc (so sánh V1 vs V2)
        (os.path.join(test_docs_dir, "hopdong_v1.docx"), "HopDong_V1"),
        (os.path.join(test_docs_dir, "hopdong_v2.docx"), "HopDong_V2"),
        # Phụ lục kho (so sánh V1 vs V2)
        (os.path.join(test_docs_dir, "phuluc_kho_v1.docx"), "PhuLuc_V1"),
        (os.path.join(test_docs_dir, "phuluc_kho_v2.docx"), "PhuLuc_V2"),
        # Hợp đồng dịch vụ bảo trì
        (os.path.join(test_docs_dir, "hopdong_dichvu_baotri.docx"), "DichVu_BaoTri"),
        # Hợp đồng lao động
        (os.path.join(test_docs_dir, "hopdong_laodong.docx"), "LaoDong"),
        # Hợp đồng mua bán thiết bị
        (os.path.join(test_docs_dir, "hopdong_muaban_thietbi.docx"), "MuaBan_ThietBi"),
    ]

    print("=" * 60)
    print("🔄 REINGEST SCRIPT — Xóa dữ liệu cũ và ingest lại")
    print("=" * 60)

    # Bước 1: Xóa ChromaDB cũ
    if os.path.exists(CHROMA_DB_PATH):
        print(f"\n[1/4] Đang xóa ChromaDB cũ tại: {CHROMA_DB_PATH}")
        try:
            shutil.rmtree(CHROMA_DB_PATH)
            print(f"      ✅ Đã xóa thành công!")
        except Exception as e:
            print(f"      [!] Lỗi khi xóa: {e}")
            print(f"      Bạn có thể xóa thủ công folder: {CHROMA_DB_PATH}")
            return
    else:
        print(f"\n[1/4] Không tìm thấy ChromaDB cũ tại: {CHROMA_DB_PATH}")

    # Bước 2: Kiểm tra files tồn tại
    print(f"\n[2/4] Kiểm tra {len(files_to_ingest)} files...")
    missing = []
    for file_path, source_name in files_to_ingest:
        if os.path.exists(file_path):
            print(f"  ✅ {source_name:20s} ← {os.path.basename(file_path)}")
        else:
            print(f"  ❌ {source_name:20s} ← {os.path.basename(file_path)} (KHÔNG TÌM THẤY)")
            missing.append(source_name)

    if missing:
        print(f"\n⚠️ Thiếu {len(missing)} files: {', '.join(missing)}")
        print("Tiếp tục ingest các file có sẵn...\n")

    # Bước 3: Re-ingest từng file
    print(f"\n[3/4] Bắt đầu re-ingest...")
    print("-" * 60)

    success_count = 0
    total_chunks = 0
    for file_path, source_name in files_to_ingest:
        if not os.path.exists(file_path):
            continue

        try:
            print(f"\n[*] Ingesting: {os.path.basename(file_path)} → source: {source_name}")
            result = ingest_document(file_path, source_name=source_name, force=True)
            num_chunks = result["num_chunks"]
            quality = result["validation"]["quality"]
            total_chunks += num_chunks
            print(f"    => ✅ OK: {num_chunks} chunks (quality={quality})")
            success_count += 1
        except Exception as e:
            print(f"    => ❌ LỖI: {e}")

    # Bước 4: Verify — liệt kê sources trong ChromaDB
    print(f"\n[4/4] VERIFY — Kiểm tra ChromaDB")
    print("=" * 60)
    try:
        collection = get_collection()
        all_data = collection.get(include=["metadatas"])
        sources = {}
        articles = {}
        for meta in all_data["metadatas"]:
            src = meta.get("source", "Unknown")
            art = meta.get("article_ref", "Unknown")
            sources[src] = sources.get(src, 0) + 1
            key = f"{src}/{art}"
            articles[key] = articles.get(key, 0) + 1

        print(f"\n📊 Tổng chunks trong ChromaDB: {len(all_data['ids'])}")
        print(f"\n📁 Sources ({len(sources)}):")
        for src, count in sorted(sources.items()):
            print(f"  {src:25s}: {count} chunks")

        print(f"\n📋 Articles (top 20):")
        for key, count in sorted(articles.items())[:20]:
            print(f"  {key:40s}: {count} chunks")
    except Exception as e:
        print(f"  ⚠️ Lỗi khi verify: {e}")

    print(f"\n{'=' * 60}")
    print(f"✅ KẾT QUẢ")
    print(f"{'=' * 60}")
    print(f"  - Thành công: {success_count}/{len(files_to_ingest)} files")
    print(f"  - Tổng chunks: {total_chunks}")
    print(f"  - ChromaDB mới: {CHROMA_DB_PATH}")
    print(f"\nBạn có thể test bằng:")
    print('  python query.py "Giá thuê nhà là bao nhiêu?" --show-chunks')
    print('  python compare.py "Điều 3" --v1 ThueNha_V1 --v2 ThueNha_V2')
    print("=" * 60 + "\n")


if __name__ == "__main__":
    clean_and_reingest()

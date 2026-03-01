import argparse
import sys
# Import đúng hàm mới từ rag_pipeline
from rag_pipeline import ingest_document

def main():
    parser = argparse.ArgumentParser(
        description="Đọc PDF/DOCX, chia nhỏ theo Điều khoản và lưu vào ChromaDB"
    )
    parser.add_argument("file_path", help="Đường dẫn tới file tài liệu (PDF hoặc DOCX) cần xử lý")
    parser.add_argument(
        "--source", "-s", default=None,
        help="Tên phiên bản tài liệu (VD: HopDong_V1)",
    )

    args = parser.parse_args()

    try:
        # Gọi hàm ingest_document thay vì ingest_pdf
        num_chunks = ingest_document(args.file_path, source_name=args.source)
        print(f"\n✅ Hoàn tất! Đã lưu {num_chunks} chunks vào ChromaDB.")
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
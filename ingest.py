import argparse
import sys
# Import đúng hàm mới từ rag_pipeline
from rag_pipeline import ingest_document

def main():
    parser = argparse.ArgumentParser(
        description="Đọc PDF/DOCX, kiểm tra chất lượng, chia nhỏ theo Điều khoản và lưu vào ChromaDB"
    )
    parser.add_argument("file_path", help="Đường dẫn tới file tài liệu (PDF hoặc DOCX) cần xử lý")
    parser.add_argument(
        "--source", "-s", default=None,
        help="Tên phiên bản tài liệu (VD: HopDong_V1)",
    )
    parser.add_argument(
        "--force", "-f", action="store_true",
        help="Bỏ qua kiểm tra chất lượng (ingest cả tài liệu LOW quality)",
    )

    args = parser.parse_args()

    try:
        result = ingest_document(args.file_path, source_name=args.source, force=args.force)
        
        quality = result["validation"]["quality"]
        score = result["validation"]["score"]
        num_chunks = result["num_chunks"]
        
        if result.get("forced"):
            print(f"\n⚠️ Hoàn tất (FORCED)! Đã lưu {num_chunks} chunks (quality={quality}, score={score}/100)")
        else:
            print(f"\n✅ Hoàn tất! Đã lưu {num_chunks} chunks vào ChromaDB (quality={quality}, score={score}/100)")
            
    except ValueError as e:
        # Validation failed
        print(f"\n❌ TỪ CHỐI: {e}", file=sys.stderr)
        print(f"\n💡 Gợi ý: Dùng --force để bỏ qua kiểm tra chất lượng.", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
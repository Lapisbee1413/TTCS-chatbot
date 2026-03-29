"""
compare.py – CLI tool để so sánh 2 phiên bản của cùng một điều khoản

Usage:
    python compare.py "Điều 5" --v1 "PhuLuc_V1" --v2 "PhuLuc_V2"
    python compare.py "Điều 5" --v1 "HopDong_V1" --v2 "HopDong_V2" --model mistral
    python compare.py "Điều 10" --v1 "V1" --v2 "V2" --show-full-text
"""

import argparse
from rag_pipeline import generate_comparison_report, QWEN_MODEL, MISTRAL_MODEL


def main():
    parser = argparse.ArgumentParser(
        description="So sánh 2 phiên bản của cùng một điều khoản với citation và nguyên tắc evidence-based"
    )
    parser.add_argument("article", help='Tên điều khoản cần so sánh (VD: "Điều 5")')
    parser.add_argument(
        "--v1", default="HopDong_V1",
        help="Tên nguồn phiên bản 1 (mặc định: HopDong_V1)",
    )
    parser.add_argument(
        "--v2", default="HopDong_V2",
        help="Tên nguồn phiên bản 2 (mặc định: HopDong_V2)",
    )
    parser.add_argument(
        "--model", "-m", default=QWEN_MODEL,
        choices=[QWEN_MODEL, MISTRAL_MODEL, "qwen2.5:3b", "qwen2.5:1.5b", "qwen2.5:7b", "mistral"],
        help=f"LLM model Ollama sử dụng (mặc định: {QWEN_MODEL})",
    )
    parser.add_argument(
        "--show-full-text", action="store_true",
        help="Hiển thị toàn bộ nội dung gốc của cả 2 phiên bản",
    )
    parser.add_argument(
        "--show-citations", action="store_true",
        help="Hiển thị danh sách trích dẫn chi tiết",
    )

    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"🔍 SO SÁNH: {args.article}")
    print(f"   V1: {args.v1}  |  V2: {args.v2}")
    print(f"   Model: {args.model}")
    print(f"{'='*60}\n")

    # Gọi hàm so sánh
    result = generate_comparison_report(
        article_name=args.article,
        source_v1=args.v1,
        source_v2=args.v2,
        model=args.model
    )

    # Hiển thị nội dung đầy đủ nếu được yêu cầu
    if args.show_full_text:
        print(f"\n{'─'*60}")
        print(f"📄 NỘI DUNG ĐẦY ĐỦ - {args.v1}")
        print(f"{'─'*60}")
        print(result['v1_text'])

        print(f"\n{'─'*60}")
        print(f"📄 NỘI DUNG ĐẦY ĐỦ - {args.v2}")
        print(f"{'─'*60}")
        print(result['v2_text'])
        print()

    # Hiển thị báo cáo so sánh
    print(f"{'─'*60}")
    print(f"📊 BÁO CÁO SO SÁNH (Powered by {result['model']})")
    print(f"{'─'*60}\n")
    print(result['comparison_report'])
    print()

    # Hiển thị citations nếu được yêu cầu
    if args.show_citations and result['citations']:
        print(f"{'─'*60}")
        print(f"📚 DANH SÁCH TRÍCH DẪN")
        print(f"{'─'*60}")
        for i, cite in enumerate(result['citations'], 1):
            print(f"\n[{i}] Nguồn: {cite['source']}, {cite['article_ref']}")
            print(f"    Trích đoạn: {cite['excerpt']}")
        print()

    # Footer
    print(f"{'='*60}")
    print(f"✅ Hoàn tất so sánh!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

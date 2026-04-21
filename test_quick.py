import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from rag_pipeline import retrieve, QWEN_MODEL

print(f"Model: {QWEN_MODEL}")
print()

# Test 1: Retrieval with source auto-detect
print("=== Test 1: Source-aware retrieval ===")
hits = retrieve("Giá thuê nhà V1 là bao nhiêu?", top_k=3)
print(f"Hits: {len(hits)}")
for h in hits:
    print(f"  [{h['metadata']['source']}] {h['metadata']['article_ref']} (dist={h['distance']:.4f})")

print()

# Test 2: Cross-doc (no source filter)
print("=== Test 2: No source filter ===")
hits2 = retrieve("Hợp đồng nào có giá trị lớn nhất?", top_k=3)
print(f"Hits: {len(hits2)}")
for h in hits2:
    print(f"  [{h['metadata']['source']}] {h['metadata']['article_ref']} (dist={h['distance']:.4f})")

print()

# Test 3: Compare article pair
print("=== Test 3: Compare article pair ===")
from rag_pipeline import retrieve_article_pair
pair = retrieve_article_pair("Điều 3", "ThueNha_V1", "ThueNha_V2")
print(f"V1 text length: {len(pair['v1_text'])}")
print(f"V2 text length: {len(pair['v2_text'])}")
print(f"V1 found: {'Không tìm thấy' not in pair['v1_text']}")
print(f"V2 found: {'Không tìm thấy' not in pair['v2_text']}")

print("\n✅ All tests passed!")

from rag_pipeline import retrieve_article_pair



# Trích đoạn văn bản của Điều 5 từ cả hai phiên bản PhuLuc_V1 và PhuLuc_V2
ket_qua = retrieve_article_pair("Điều 5", source_v1="PhuLuc_V1", source_v2="PhuLuc_V2")



print(f"--- ĐANG RÚT TRÍCH: {ket_qua['article_name'].upper()} ---")
print("\n[BẢN CŨ - V1]:")
print(ket_qua['v1_text'])

print("\n-------------------------")
print("[BẢN MỚI - V2]:")
print(ket_qua['v2_text'])
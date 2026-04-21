# BAO CAO TIEN DO TUAN 11: QUALITY IMPROVEMENT (BAN CHOT)

Thoi gian: 2026-04-14 -> 2026-04-20  
Muc tieu: Cai tien retrieval va prompt de tang do on dinh, giam hallucination, tang citation/comparison quality  
Deadline: 21/4/2026

---

## 1) Ket qua da hoan thanh

### 1.1 Dong bo model runtime sang qwen2.5:3b
- Backend schema mac dinh da dung qwen2.5:3b.
- Frontend API client mac dinh da dung qwen2.5:3b.
- Script test va tai lieu huong dan da cap nhat theo qwen2.5:3b.

### 1.2 Nang cap retrieval logic
- Da fix luong source_filter: loc nguon truoc khi tao prompt/generate.
- Da bo fallback nguy hiem (khong con tu y search all sources khi source_filter loi).
- Da them hybrid rerank (dense + lexical overlap + intent bonus).
- Da them co che da dang hoa nguon cho cau hoi cross-document.

### 1.3 Prompt va answer behavior
- Prompt can bang hon: giam over-refusal, nhung van giu nguyen tac khong bang chung thi khong ket luan.
- Van giu citation requirement va khung tra loi cho compare.

### 1.4 Danh gia round2 va round3
- Da co ket qua danh gia round2.
- Da chay tiep round3 sau khi implement retrieval vong moi.

---

## 2) So sanh chi so (Baseline vs Round2 vs Round3)

| Metric | Baseline | Round2 | Round3 | Nhan xet |
|---|---:|---:|---:|---|
| Retrieval Accuracy | 0.2595 | 0.2216 | 0.2459 | Round3 phuc hoi 1 phan, nhung chua vuot baseline |
| Answer Relevance | 0.6852 | 0.5284 | 0.7165 | Round3 da vuot baseline |
| Citation Accuracy | 0.1333 | 0.6667 | 0.6889 | Cai tien manh va on dinh |
| Hallucination (unanswerable) | 0.7500 | 0.0000 | 0.5000 | Tot hon baseline, nhung chua bang round2 |
| Compare Completeness | 0.0833 | 0.5250 | 0.7083 | Cai tien rat manh |
| Overall Score | 0.3823 | 0.3883 | 0.5719 | Tang ro ret sau round3 |

Ket luan tong quan tuan 11:
- Da cai thien rat ro o chat luong tong the, citation accuracy, compare completeness.
- Relevance da dat muc cao hon baseline.
- Retrieval accuracy van la diem can toi uu them trong tuan 12.

---

## 3) Cach tu tay test toan bo he thong (end-to-end)

### 3.1 Chuan bi moi truong
1. Chay Ollama:
  - ollama pull qwen2.5:3b
  - ollama serve
2. Cai dependencies:
  - pip install -r requirements.txt
  - cd backend && pip install -r requirements.txt && cd ..
  - cd frontend && npm install && cd ..

### 3.2 Reingest du lieu mau
1. python reingest.py
2. Kiem tra output:
  - Co list sources day du
  - Co tong chunks > 0

### 3.3 Test backend API
1. Chay backend:
  - start_backend.bat
2. Chay API smoke test:
  - cd backend
  - python test_api.py
  - cd ..
3. Tieu chi pass:
  - /api/query tra ve success=true
  - /api/compare tra ve report co noi dung

### 3.4 Test frontend
1. Chay frontend:
  - start_frontend.bat
2. Test tay tren UI:
  - Upload 2-3 tai lieu
  - Hoi factual (vd: gia thue, thoi han)
  - Hoi cross-doc (vd: hop dong nao gia tri lon nhat)
  - Chay compare dieu khoan (vd: Dieu 3 V1 vs V2)
3. Tieu chi pass:
  - UI khong crash
  - Co citation trong cau tra loi
  - Compare co cau truc ro rang

### 3.5 Test CLI/integration
1. python test_quick.py
2. node integration_test.js
3. python compare.py "Dieu 3" --v1 ThueNha_V1 --v2 ThueNha_V2

### 3.6 Test evaluation (bao cao dinh luong)
1. Chay danh gia:
  - python evaluation/evaluate.py --model qwen2.5:3b --tag round3
2. Tao bao cao so sanh:
  - python evaluation/improvement_report.py --improved evaluation/round3_results.json --output evaluation/comparison_round3.json
3. File can nop:
  - evaluation/round3_results.json
  - evaluation/comparison_round3.json

---

## 4) Tra loi cau hoi: Neu thay dua van ban moi thi co ung nghiem khong?

Tra loi ngan gon: Co the ung nghiem, NHUNG can test voi bo van ban unseen truoc khi ket luan chat luong cuoi.

Giai thich:
- Baseline/round2/round3 hien tai la danh gia tren bo tai lieu va bo cau hoi da xay dung trong project.
- He thong RAG nay ve kien truc la mo: ingest tai lieu moi -> chunk -> embed -> retrieve -> answer co citation.
- Vi vay ve mat co che, van ban moi van chay duoc.
- Tuy nhien do chinh xac se phu thuoc vao:
  - Chat luong text extraction (PDF scan, OCR, bang bieu)
  - Cau truc van ban (co ro dieu/khoan hay khong)
  - Muc do khac biet thuat ngu so voi du lieu huan luyen/evaluation hien tai

### 4.1 Protocol test nhanh voi van ban moi (khuyen nghi cho buoi demo voi thay)
1. Lay 2-3 van ban moi (unseen), ingest vao he thong.
2. Tao 20-30 cau hoi tay, gom 5 nhom:
  - factual
  - multi-article
  - cross-document
  - comparison
  - unanswerable
3. Cham theo 4 tieu chi:
  - Tra loi dung/noi dung
  - Co citation dung nguon
  - Co hallucination hay khong
  - Do day du cua so sanh
4. Neu can tra loi bao cao nhanh:
  - Neu citation dung va hallucination thap, co the xem la ung nghiem tot cho van ban moi cung domain.

---

## 5) Rui ro con lai va huong toi uu Tuan 12

1. Retrieval accuracy chua vuot baseline.
2. Mot so cau cross-document van nhieu noise context.
3. Hallucination da giam so voi baseline nhung can tiep tuc giam.

Huong toi uu Tuan 12:
1. Them query intent classifier nhe de chon strategy retrieval theo loai cau hoi.
2. Them rerank stage manh hon (cross-encoder hoac rule-based boost theo article/field).
3. Them bo unseen-doc benchmark rieng de bao ve chat luong khi gap van ban moi.

---

## 6) Deliverables Tuan 11

- Code retrieval/prompt da cap nhat trong rag_pipeline.py.
- evaluation/round2_results.json
- evaluation/comparison_report.json
- evaluation/round3_results.json
- evaluation/comparison_round3.json
- Report/PROGRESS_W11.md (ban chot)

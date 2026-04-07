# Test Documents Summary

## ✅ Đã tạo thành công 5 file DOCX test

Tất cả các file đã được tạo trong thư mục `test_documents/`:

### 1. **hopdong_thue_nha_v1.docx** (Hợp đồng thuê nhà - V1)
- **Mục đích**: Test upload, query, và làm baseline cho so sánh phiên bản
- **Nội dung chính**:
  - Giá thuê: 5.000.000 VNĐ/tháng
  - Thời hạn: 12 tháng (01/02/2024 - 31/01/2025)
  - Diện tích: 50m²
  - Nội thất: Cơ bản
  - Tiền cọc: 10.000.000 VNĐ
  - Thanh toán: Ngày 05 hàng tháng
- **Test queries**:
  - "Giá thuê nhà là bao nhiêu?"
  - "Thời hạn hợp đồng bao lâu?"
  - "Trách nhiệm của bên cho thuê là gì?"

### 2. **hopdong_thue_nha_v2.docx** (Hợp đồng thuê nhà - V2)
- **Mục đích**: So sánh với V1 để test chức năng compare
- **Thay đổi so với V1**:
  - ✏️ Giá thuê: 6.000.000 VNĐ/tháng (+1M)
  - ✏️ Thời hạn: 24 tháng (dài gấp đôi)
  - ✏️ Nội thất: Cao cấp (thêm tủ lạnh, máy giặt, điều hòa)
  - ✏️ Tiền cọc: 12.000.000 VNĐ (+2M)
  - ✏️ Thanh toán: Ngày 01 hàng tháng (thay đổi từ ngày 05)
  - ➕ **MỚI**: Chi phí dịch vụ 500.000 VNĐ/tháng
  - ➕ **MỚI**: Quyền chấm dứt sớm (báo trước 2 tháng)
  - ➕ **MỚI**: Trách nhiệm sửa chữa của bên A
  - ➕ **MỚI**: Bảo hiểm cháy nổ của bên B
  - ✏️ Không tăng giá trong 12 tháng đầu (thay vì không tăng giá trong toàn bộ hợp đồng)
- **Test compare**:
  - So sánh ĐIỀU 3 (giá thuê và thanh toán)
  - So sánh ĐIỀU 4 (thời hạn)
  - So sánh ĐIỀU 5 và 6 (trách nhiệm các bên)

### 3. **hopdong_dichvu_baotri.docx** (Hợp đồng dịch vụ bảo trì IT)
- **Mục đích**: Test với tài liệu khác domain (technical services)
- **Nội dung chính**:
  - Giá trị: 120.000.000 VNĐ/năm (30M/quý)
  - Dịch vụ: Bảo trì server, backup, bảo mật, hỗ trợ 24/7
  - SLA: 99.5% uptime
  - Thời gian phản hồi: Khẩn cấp 1h, thường 4h
  - Phạt nếu vi phạm SLA
- **Test queries**:
  - "SLA của hợp đồng là gì?"
  - "Thời gian phản hồi sự cố khẩn cấp?"
  - "Giá trị hợp đồng bao nhiêu mỗi năm?"

### 4. **hopdong_laodong.docx** (Hợp đồng lao động)
- **Mục đích**: Test với HR documents
- **Nội dung chính**:
  - Vị trí: Lập trình viên Frontend
  - Lương: 15.000.000 VNĐ/tháng (thử việc 85% = 12.750.000)
  - Phụ cấp: Ăn trưa 1M, xăng 500K, điện thoại 300K
  - Thời hạn: 24 tháng với 60 ngày thử việc
  - Giờ làm: 8:00-17:00, nghỉ trưa 12:00-13:00
  - Nghỉ phép: 12 ngày/năm
- **Test queries**:
  - "Lương của lập trình viên là bao nhiêu?"
  - "Có những phụ cấp gì?"
  - "Thời gian thử việc bao lâu?"

### 5. **hopdong_muaban_thietbi.docx** (Hợp đồng mua bán thiết bị)
- **Mục đích**: Test với structured data (tables)
- **Nội dung chính**:
  - Tổng giá trị: 220.000.000 VNĐ (bao gồm VAT)
  - Bảng danh sách thiết bị (5 items)
  - Thanh toán: 3 đợt (30% - 60% - 10%)
  - Bảo hành: 24 tháng
  - Lắp đặt miễn phí
- **Test queries**:
  - "Có bao nhiêu thiết bị được mua?"
  - "Thời gian bảo hành là bao lâu?"
  - "Thanh toán như thế nào?"

## 🎯 Kịch bản test đầy đủ

### Scenario 1: Upload và Query cơ bản
1. Upload `hopdong_thue_nha_v1.docx` với source name "ThueNha_V1"
2. Hỏi: "Giá thuê là bao nhiêu?" → Expect: 5.000.000 VNĐ/tháng
3. Hỏi: "Điều 3 quy định gì?" → Expect: Giá thuê và phương thức thanh toán
4. Kiểm tra citations có hiển thị đúng không

### Scenario 2: So sánh phiên bản (Core feature của Week 7-8)
1. Upload cả `hopdong_thue_nha_v1.docx` và `hopdong_thue_nha_v2.docx`
2. Vào trang Compare
3. Chọn article: "ĐIỀU 3"
4. Chọn version 1: ThueNha_V1, version 2: ThueNha_V2
5. Click "So sánh"
6. **Expect kết quả**:
   - Giá thay đổi: 5M → 6M
   - Tiền cọc: 10M → 12M
   - Ngày thanh toán: 05 → 01
   - Phí dịch vụ mới được thêm vào

### Scenario 3: Parallel View
1. Upload 2 hợp đồng khác loại: `hopdong_thue_nha_v1.docx` và `hopdong_laodong.docx`
2. Vào trang Parallel View
3. Chọn Document 1: ThueNha_V1, Document 2: LaoDong
4. Xem song song 2 tài liệu
5. Test synchronized scrolling (cuộn bên trái, bên phải tự cuộn theo)
6. Test highlighting differences

### Scenario 4: Chat với nhiều tài liệu
1. Upload tất cả 5 tài liệu
2. Chat: "Tài liệu nào có quy định về giá cả?"
3. Chat: "So sánh các khoản phí/chi phí trong các hợp đồng"
4. Chat: "Hợp đồng nào có thời hạn dài nhất?"
5. Kiểm tra citations từ nhiều nguồn

### Scenario 5: Truy vấn kỹ thuật
1. Upload `hopdong_dichvu_baotri.docx`
2. Chat: "SLA là gì?"
3. Chat: "Nếu uptime chỉ đạt 96% thì sao?"
4. Chat: "Dịch vụ bao gồm những gì?"

### Scenario 6: Truy vấn structured data
1. Upload `hopdong_muaban_thietbi.docx`
2. Chat: "Liệt kê các thiết bị được mua"
3. Chat: "Tổng giá trị từng đợt thanh toán là bao nhiêu?"
4. Kiểm tra RAG có extract được data từ table không

## 📊 Expected Results

### Upload
- ✅ File được accept (.docx)
- ✅ Progress bar hiển thị
- ✅ Success message với source name
- ✅ File xuất hiện trong danh sách documents

### Query/Chat
- ✅ Câu trả lời chính xác dựa trên nội dung tài liệu
- ✅ Citations hiển thị đúng (source + article/section)
- ✅ Không có hallucination (không bịa thông tin)
- ✅ Response time < 5s (với Ollama local)

### Compare
- ✅ Phát hiện tất cả thay đổi quan trọng
- ✅ Format rõ ràng: Modified/Added/Removed/Unchanged
- ✅ Trích dẫn cả 2 phiên bản
- ✅ Báo cáo dễ đọc

### Parallel View
- ✅ 2 documents load đầy đủ
- ✅ Synchronized scrolling hoạt động
- ✅ Highlighting differences (nếu có)
- ✅ UI responsive, không lag

## 🔍 Debugging Tips

Nếu gặp vấn đề:

**1. Upload không thành công**
- Kiểm tra backend đã chạy: http://localhost:8000/docs
- Kiểm tra CORS settings
- Xem console log ở browser DevTools

**2. Query không trả lời đúng**
- Kiểm tra ChromaDB đã ingest đúng chưa: `ls chroma_db/`
- Test CLI: `python query.py "câu hỏi"`
- Kiểm tra model Ollama: `ollama list`

**3. Compare không hoạt động**
- Kiểm tra 2 source names khác nhau
- Kiểm tra article name tồn tại trong cả 2 documents
- Test CLI: `python compare.py "ĐIỀU 3" --source1 ThueNha_V1 --source2 ThueNha_V2`

**4. Frontend lỗi**
- Check backend API: http://localhost:8000/api/documents
- Check browser console
- Check network tab (XHR requests)

## 💡 Next Steps

Sau khi test thành công Week 9:

1. **Week 10**: Tạo evaluation dataset
   - Chuẩn bị câu hỏi + câu trả lời chuẩn
   - Chạy baseline với các câu hỏi này
   - Đánh giá accuracy, relevance

2. **Week 11**: Cải tiến chất lượng
   - Tune chunking strategy
   - Thử different retrieval methods
   - Optimize prompts
   - Reduce hallucination

3. **Week 12**: Hoàn thiện & demo
   - Polish UI/UX
   - Tạo slide thuyết trình
   - Record demo video
   - Viết báo cáo cuối cùng

## 📝 Notes

- Tất cả test files đều bằng tiếng Việt để phù hợp với use case thực tế
- Nội dung có cấu trúc pháp lý chuẩn (Điều, khoản, mục)
- Cover nhiều domain: Real estate, IT services, HR, Procurement
- V1/V2 pairs có meaningful differences để test compare feature
- Có thể tạo thêm test files bằng cách chạy `python create_test_docs.py`
- Nếu cần test PDF: Cài `pip install reportlab` rồi chạy `python create_test_pdf.py`

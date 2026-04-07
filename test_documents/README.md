# Test Documents

Folder này chứa các file hợp đồng mẫu bằng tiếng Việt để test đầy đủ các tính năng của RAG chatbot.

## Files

### File gốc (Original)
- `hopdong_v1.docx` - Hợp đồng phiên bản 1
- `hopdong_v2.docx` - Hợp đồng phiên bản 2
- `phuluc_kho_v1.docx` - Phụ lục kho phiên bản 1
- `phuluc_kho_v2.docx` - Phụ lục kho phiên bản 2

### File test mới (Created with create_test_docs.py)

**1. Hợp đồng thuê nhà (để test so sánh phiên bản)**
- `hopdong_thue_nha_v1.docx`: Phiên bản 1
  - Giá thuê: 5.000.000 VNĐ/tháng
  - Thời hạn: 12 tháng
  - Nội thất cơ bản
  
- `hopdong_thue_nha_v2.docx`: Phiên bản 2 (có thay đổi)
  - Giá thuê: 6.000.000 VNĐ/tháng (THAY ĐỔI)
  - Thời hạn: 24 tháng (THAY ĐỔI)
  - Nội thất cao cấp (THAY ĐỔI)
  - Thêm phí dịch vụ (MỚI)
  - Thay đổi điều khoản thanh toán (THAY ĐỔI)

**2. Hợp đồng dịch vụ**
- `hopdong_dichvu_baotri.docx`: Hợp đồng bảo trì hệ thống IT
  - Giá trị: 120.000.000 VNĐ/năm
  - SLA: 99.5% uptime
  - Hỗ trợ 24/7
  - Test thuật ngữ kỹ thuật

**3. Hợp đồng lao động**
- `hopdong_laodong.docx`: Hợp đồng tuyển dụng
  - Vị trí: Lập trình viên Frontend
  - Thông tin lương, phúc lợi
  - Giờ làm việc, nghỉ phép
  - Test câu hỏi về nhân sự

**4. Hợp đồng mua bán**
- `hopdong_muaban_thietbi.docx`: Hợp đồng mua bán thiết bị
  - Bán thiết bị công nghiệp
  - Thanh toán 3 đợt
  - Có bảng danh sách thiết bị
  - Test trích xuất dữ liệu có cấu trúc

## Kịch bản test

### 1. Upload & Query
Upload tài liệu bất kỳ và hỏi:
- "Giá thuê là bao nhiêu?"
- "Thời hạn hợp đồng là bao lâu?"
- "Trách nhiệm của bên A là gì?"

### 2. So sánh phiên bản
So sánh `hopdong_thue_nha_v1.docx` vs `hopdong_thue_nha_v2.docx`:
- Thay đổi giá (5M → 6M)
- Thay đổi thời hạn (12 tháng → 24 tháng)
- Điều khoản mới được thêm
- Điều khoản đã sửa đổi

### 3. Xem song song
Xem 2 hợp đồng khác nhau cùng lúc:
- So sánh hợp đồng thuê nhà vs hợp đồng lao động
- So sánh hợp đồng dịch vụ vs hợp đồng mua bán

### 4. Kiểm tra trích dẫn
Hỏi câu hỏi cụ thể và kiểm tra citation:
- "Điều 3 nói về gì?"
- "Có quy định về bảo hành không?"

### 5. Truy vấn đa tài liệu
Upload nhiều tài liệu và hỏi:
- "Tài liệu nào có thông tin về giá cả?"
- "So sánh các khoản thanh toán"

## Cách sử dụng

### Web UI (khuyên dùng) ✅
1. Mở http://localhost:5173/upload
2. Drag & drop file vào
3. Đặt tên source (VD: HopDong_V1)
4. Click Upload

### CLI (legacy)
```bash
# Upload từ folder này
python ingest.py test_documents/hopdong_thue_nha_v1.docx --source "ThueNha_V1"
python ingest.py test_documents/hopdong_thue_nha_v2.docx --source "ThueNha_V2"
```

## Tạo thêm tài liệu test

Chạy script để tạo lại hoặc thêm tài liệu mới:
```bash
python create_test_docs.py
```

Script sẽ tạo các hợp đồng tiếng Việt có:
- Định dạng và cấu trúc chuẩn
- Nhiều điều khoản chi tiết
- Bảng và chữ ký
- Nội dung thực tế để test

## Lưu ý

- Tất cả tài liệu đều bằng tiếng Việt để test thực tế
- Các file có cấu trúc hợp đồng pháp lý đúng chuẩn
- Cặp phiên bản (v1/v2) có sự khác biệt rõ ràng để test so sánh
- Tài liệu cover nhiều lĩnh vực (thuê nhà, lao động, dịch vụ, mua bán)
- Dùng Web UI để upload (không cần di chuyển file ra folder gốc)

# 🎓 User Guide - RAG Legal Chatbot

## 📖 Mục Lục
1. [Giới thiệu](#giới-thiệu)
2. [Cài đặt](#cài-đặt)
3. [Khởi động ứng dụng](#khởi-động-ứng-dụng)
4. [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
5. [Tính năng nâng cao](#tính-năng-nâng-cao)
6. [Troubleshooting](#troubleshooting)

---

## 🌟 Giới thiệu

RAG Legal Chatbot là ứng dụng AI hỗ trợ phân tích tài liệu pháp lý với:
- ✅ Upload tài liệu PDF/DOCX
- ✅ Hỏi đáp với trích dẫn nguồn
- ✅ So sánh 2 phiên bản tài liệu
- ✅ Xem song song (parallel view)
- ✅ Nguyên tắc "Không bằng chứng → Không kết luận"

---

## 🔧 Cài đặt

### Yêu cầu hệ thống
- **Python:** 3.8 trở lên
- **Node.js:** 16 trở lên
- **Ollama:** Latest version
- **RAM:** Tối thiểu 8GB (khuyên dùng 16GB)
- **Disk:** 10GB trống

### Bước 1: Cài đặt Ollama

```bash
# Download từ: https://ollama.com
# Sau khi cài đặt, pull models:

ollama pull qwen2.5:1.5b
ollama pull mistral

# Khởi động Ollama (giữ terminal này chạy)
ollama serve
```

### Bước 2: Cài đặt Python dependencies

```bash
# Tại thư mục gốc project
pip install -r requirements.txt

# Cài đặt backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### Bước 3: Cài đặt Frontend dependencies

```bash
cd frontend
npm install
cd ..
```

---

## 🚀 Khởi động ứng dụng

### Cách 1: Sử dụng Batch Files (Windows)

**Terminal 1 - Backend:**
```bash
start_backend.bat
```

**Terminal 2 - Frontend:**
```bash
start_frontend.bat
```

### Cách 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Truy cập ứng dụng

- 🌐 **Frontend UI:** http://localhost:5173
- 🔧 **Backend API:** http://localhost:8000
- 📖 **API Docs:** http://localhost:8000/docs

---

## 📚 Hướng dẫn sử dụng

### 1️⃣ Upload Tài liệu

1. Mở http://localhost:5173
2. Click vào **"Upload"** trong menu bên trái
3. Click **"Select File"** hoặc drag & drop file
4. Nhập tên nguồn (VD: `HopDong_V1`, `PhuLuc_V2`)
5. Click **"Upload"**

**Lưu ý:**
- Chỉ hỗ trợ PDF và DOCX
- Kích thước tối đa: 10MB
- Tên nguồn nên đặt có ý nghĩa để dễ phân biệt

**Kết quả:**
```
✅ Success!
Document: hopdong_v1.docx
Source: HopDong_V1
Chunks created: 45
```

---

### 2️⃣ Chat & Query (Hỏi đáp)

1. Click **"Chat"** trong menu
2. Nhập câu hỏi vào ô input
3. Click **"Send"** hoặc nhấn Enter

**Ví dụ câu hỏi:**
- "Điều 5 quy định gì?"
- "Nghĩa vụ của bên A là gì?"
- "So sánh Điều 3 và Điều 5"

**Kết quả:**
- Câu trả lời chi tiết
- Citations (trích dẫn nguồn) dạng chips
- Chat history được lưu

**Citations:**
```
[HopDong_V1 - Điều 5]  [PhuLuc_V2 - Điều 3]
```

---

### 3️⃣ Compare (So sánh phiên bản)

1. Click **"Compare"** trong menu
2. Nhập tên điều khoản (VD: `Điều 5`)
3. Chọn Version 1 từ dropdown
4. Chọn Version 2 từ dropdown
5. Click **"Compare"**

**Kết quả:**
- **Nội dung V1:** Toàn bộ text của Điều X từ V1
- **Nội dung V2:** Toàn bộ text của Điều X từ V2
- **Comparison Report:** Phân tích chi tiết sự khác biệt
  - Điểm giống nhau
  - Điểm khác nhau
  - Tóm tắt thay đổi

---

### 4️⃣ Parallel View (Xem song song)

1. Click **"Parallel View"** trong menu
2. Chọn Version 1 từ dropdown bên trái
3. Chọn Version 2 từ dropdown bên phải
4. Bật **"Sync Scroll"** để đồng bộ cuộn

**Tính năng:**
- ✅ Xem 2 phiên bản cạnh nhau
- ✅ Synchronized scrolling (khi bật)
- ✅ Color-coded differences:
  - **Gray:** Nội dung giống nhau
  - **Orange:** Nội dung đã sửa đổi
  - **Green:** Nội dung thêm mới (V2)
  - **Red:** Nội dung đã xóa (V2)

---

## 🎨 Tính năng nâng cao

### Evidence-based Answering

Chatbot tuân thủ nghiêm ngặt nguyên tắc:
> **"Không bằng chứng → Không kết luận"**

**Ví dụ:**
```
Q: "Điều 10 quy định gì?"
A: "Không tìm thấy thông tin về Điều 10 trong cơ sở dữ liệu."

(Thay vì đoán mò hoặc bịa thông tin)
```

### Citation System

Mọi thông tin đều có trích dẫn nguồn:
```
[Nguồn: HopDong_V1, Điều 5]
```

Click vào citation chip để xem chi tiết chunk.

### Multi-model Support

Hỗ trợ nhiều LLM models:
- **qwen2.5:1.5b** (default - nhanh)
- **mistral** (chất lượng cao hơn, chậm hơn)

Để đổi model, sử dụng CLI:
```bash
python query.py "Câu hỏi?" --model mistral
```

---

## 🛠️ Troubleshooting

### Backend không khởi động được

**Lỗi:** `ModuleNotFoundError: No module named 'fastapi'`
```bash
cd backend
pip install -r requirements.txt
```

**Lỗi:** `Address already in use (port 8000)`
```bash
# Kill process trên port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

### Frontend không kết nối được backend

**Kiểm tra:**
1. Backend có đang chạy không? → http://localhost:8000/health
2. CORS có được bật không? → Kiểm tra `backend/app/main.py`

**Fix:**
```javascript
// frontend/src/config.js
export const API_BASE_URL = 'http://localhost:8000'
```

### Ollama không hoạt động

**Lỗi:** `Connection refused to Ollama`

**Fix:**
```bash
# Khởi động Ollama
ollama serve

# Kiểm tra models đã pull chưa
ollama list

# Pull models nếu chưa có
ollama pull qwen2.5:1.5b
ollama pull mistral
```

### Upload file bị lỗi

**Lỗi:** `Invalid file type`
- ✅ Chỉ hỗ trợ: `.pdf`, `.docx`
- ❌ Không hỗ trợ: `.doc`, `.txt`, `.odt`

**Lỗi:** `File size must be less than 10MB`
- Giảm kích thước file hoặc tăng limit trong `backend/app/routers/upload.py`

### Chat không trả lời

**Nguyên nhân:**
1. Chưa upload tài liệu nào
2. Ollama chưa chạy
3. Model chưa được pull

**Fix:**
1. Upload ít nhất 1 tài liệu
2. Chạy `ollama serve`
3. Chạy `ollama pull qwen2.5:1.5b`

---

## 📞 Hỗ trợ

### Logs

**Backend logs:**
- Terminal chạy `uvicorn` sẽ hiển thị mọi request
- Check HTTP status codes: 200 = OK, 400 = Bad Request, 500 = Server Error

**Frontend logs:**
- Mở Chrome DevTools (F12)
- Tab "Console" để xem errors
- Tab "Network" để xem API calls

### Test API

```bash
# Test health
curl http://localhost:8000/health

# Test list documents
curl http://localhost:8000/api/documents

# Test query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Test?"}'
```

### Integration Tests

```bash
# Chạy full integration test
node integration_test.js
```

---

## 🎉 Hoàn tất!

Bạn đã sẵn sàng sử dụng RAG Legal Chatbot!

**Next steps:**
1. Upload một vài tài liệu mẫu
2. Thử chat với các câu hỏi
3. So sánh 2 phiên bản
4. Khám phá parallel view

**Chúc bạn sử dụng hiệu quả!** 🚀

# 📸 Screenshots - RAG Legal Chatbot

## 1. Home Page
**Trang chủ với 4 tính năng chính**

```
┌─────────────────────────────────────────────────────────┐
│  RAG Legal Chatbot                                      │
├─────────────────────────────────────────────────────────┤
│  Legal Document RAG Chatbot                             │
│  An AI-powered chatbot for legal document analysis      │
│  with citation support.                                 │
│                                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │  Upload  │ │   Chat   │ │ Parallel │ │ Compare  │    │
│  │ Documents│ │ & Query  │ │   View   │ │ Versions │    │
│  │    📤   │ │    💬    │ │    📊   │ │    🔄    │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- Clean, modern design với Material-UI
- 4 feature cards với icons
- Hover effect (scale 1.05)

---

## 2. Upload Page
**Upload tài liệu PDF/DOCX**

```
┌─────────────────────────────────────────────────────────┐
│  Upload Document                                        │
├─────────────────────────────────────────────────────────┤
│  Upload a PDF or DOCX legal document to add it to      │
│  the knowledge base                                     │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │         📁 Select File                          │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ℹ Selected: hopdong_v1.docx (245.67 KB)               │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Source Name (optional)                          │   │
│  │ HopDong_V1                                      │   │
│  └─────────────────────────────────────────────────┘   │
│  e.g., HopDong_V1, PhuLuc_V2                           │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │                Upload                           │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ✅ Success! Document uploaded and processed            │
│     Document: hopdong_v1.docx                           │
│     Source: HopDong_V1                                  │
│     Chunks created: 45                                  │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- Drag & drop support
- File validation (type + size)
- Progress indicator
- Success message với details

---

## 3. Chat Page
**Hỏi đáp với citations**

```
┌─────────────────────────────────────────────────────────┐
│  Chat & Query                                           │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐   │
│  │  You:                                           │   │
│  │  Điều 5 quy định gì?                           │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Chatbot:                                       │   │
│  │  Điều 5 quy định về nghĩa vụ của Bên A trong   │   │
│  │  việc cung cấp tài liệu và thông tin liên quan │   │
│  │  đến hợp đồng...                                │   │
│  │  ─────────────────────────────────────────      │   │
│  │  Citations:                                     │   │
│  │  [HopDong_V1 - Điều 5] [PhuLuc_V2 - Điều 3]   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ┌─────────────────────────────────┐ ┌──────────┐      │
│  │ Ask a question...               │ │  Send 📤 │      │
│  └─────────────────────────────────┘ └──────────┘      │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- Real-time chat interface
- User messages (blue background)
- Bot responses (white background)
- Citation chips (clickable)
- Chat history
- Auto-scroll to bottom

---

## 4. Parallel View
**Xem song song 2 phiên bản**

```
┌─────────────────────────────────────────────────────────┐
│  Parallel View                                          │
├─────────────────────────────────────────────────────────┤
│  Version 1 ▼          [🔄 Sync Scroll]     Version 2 ▼ │
│  HopDong_V1                                 HopDong_V2  │
│  ┌─────────────────────┐ ┌─────────────────────┐       │
│  │ HopDong_V1          │ │ HopDong_V2          │       │
│  │ ─────────────       │ │ ─────────────       │       │
│  │ Điều 1              │ │ Điều 1              │       │
│  │ Nội dung giống...   │ │ Nội dung giống...   │       │
│  │ (gray background)   │ │ (gray background)   │       │
│  │                     │ │                     │       │
│  │ Điều 2              │ │ Điều 2              │       │
│  │ Nội dung sửa đổi... │ │ Nội dung mới...     │       │
│  │ (orange border)     │ │ (orange border)     │       │
│  │                     │ │                     │       │
│  │ Điều 3              │ │ Điều 3              │       │
│  │ (red - removed)     │ │ (green - added)     │       │
│  └─────────────────────┘ └─────────────────────┘       │
│                                                          │
│  ℹ Color Legend:                                        │
│     Gray = Same | Orange = Modified |                   │
│     Green = Added | Red = Removed                       │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- Side-by-side comparison
- Synchronized scrolling (toggle)
- Color-coded differences
- Bordered when sync enabled

---

## 5. Compare Page
**So sánh chi tiết điều khoản**

```
┌─────────────────────────────────────────────────────────┐
│  Compare Versions                                       │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐   │
│  │ Article Name: Điều 5                           │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  Version 1 ▼                     Version 2 ▼            │
│  HopDong_V1                      HopDong_V2             │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │            🔄 Compare                           │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ✅ Comparison completed successfully                   │
│                                                          │
│  ┌──────────────────┐ ┌──────────────────┐             │
│  │ HopDong_V1       │ │ HopDong_V2       │             │
│  │ Điều 5: Bên A... │ │ Điều 5: Bên A... │             │
│  └──────────────────┘ └──────────────────┘             │
│                                                          │
│  ────────────────────────────────────────               │
│                                                          │
│  Comparison Report                                      │
│  • Nội dung V1: [chi tiết]                             │
│  • Nội dung V2: [chi tiết]                             │
│  • Điểm giống nhau: [...]                              │
│  • Điểm khác biệt: [...]                               │
│  • Tóm tắt: Điều 5 đã được sửa đổi...                 │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- Article input
- Version selectors
- Side-by-side content view
- Detailed comparison report
- Structured output

---

## 6. Navigation Sidebar

```
┌──────────────────┐
│ RAG Legal Chatbot│
├──────────────────┤
│ > 🏠 Home       │  (selected)
│   📤 Upload     │
│   💬 Chat       │
│   📊 Parallel   │
│   🔄 Compare    │
└──────────────────┘
```

**Features:**
- Fixed left sidebar
- Active item highlighting
- Icon + label
- Smooth navigation

---

## Technical Details

**Frontend:**
- React 18 + Vite
- Material-UI v5
- React Router v6
- Responsive design

**Backend:**
- FastAPI
- ChromaDB
- Ollama (Qwen 2.5 / Mistral)

**Key UI Features:**
- ✅ Loading states (spinners)
- ✅ Error boundaries
- ✅ Toast notifications
- ✅ Empty states
- ✅ Form validation
- ✅ Color-coded diff
- ✅ Responsive layout

---

## Color Scheme

**Primary:** #1976d2 (Blue)
**Secondary:** #dc004e (Pink/Red)
**Success:** #4caf50 (Green)
**Warning:** #ff9800 (Orange)
**Error:** #f44336 (Red)
**Background:** #f5f5f5 (Light Gray)

---

**Để chụp screenshots thực tế:**
1. Khởi động app: `start_backend.bat` + `start_frontend.bat`
2. Truy cập: http://localhost:5173
3. Dùng Snipping Tool hoặc PrtScn
4. Crop và save vào folder `screenshots/`

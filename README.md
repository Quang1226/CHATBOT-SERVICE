# VNJ Chatbot Service (Chatbot Chăm sóc Khách hàng trực tuyến)

> Dự án gồm **Backend (FastAPI)** + **Frontend (React/Vite)**.
> Chatbot trả lời dựa trên **FAQ trong CSDL** (RAG dạng keyword match) và gọi LLM qua **Groq (OpenAI-compatible)**.

---

## 1. Tổng quan dự án

**VNJ Chatbot Service** cung cấp:

### 1) Chatbot cho Khách hàng (Public)
- Tạo phiên chat (`conversation`) và `session_id` (UUID)
- Nhận tin nhắn từ khách hàng
- Lưu lịch sử tin nhắn vào CSDL
- Sinh phản hồi qua LLM (Groq) dựa trên tập FAQ đang bật `is_active` trong DB

### 2) Trang Admin quản lý tri thức & khai thác khách hàng tiềm năng
- Admin đăng nhập bằng username/password
- Được cấp JWT token
- Quản lý CRUD FAQ (thêm/sửa/xóa)
- Khai thác “Leads” (khách hàng để lại SĐT/Email) qua API `/api/v1/chat/leads`
- Xem lịch sử chat theo conversation qua API `/api/v1/chat/history/{conversation_id}`
- FAQ ảnh hưởng trực tiếp đến prompt chatbot


---

## 2. Kiến trúc tổng thể

### Luồng Chat
1. Frontend gọi **POST** `/api/v1/chat/start` → Backend tạo `Conversation` và trả `session_id`.
2. Frontend gọi **POST** `/api/v1/chat/message` với `session_id` + `message_text`.
3. Backend:
   - Lưu tin nhắn của user vào bảng `messages`
   - Lấy FAQ active từ bảng `faq_knowledge_base` và build `context_text`
   - (Tùy chọn) lấy một phần history hội thoại từ bảng `messages`
   - gọi LLM Groq để sinh câu trả lời
   - lưu tin nhắn của bot vào DB
4. Backend trả `MessageResponse` để frontend render.

### Luồng Admin
- Admin login tại `/api/v1/auth/login` → nhận JWT.
- Các API FAQ đều yêu cầu JWT qua header `Authorization: Bearer <token>`.
- Ngoài FAQ, Admin còn gọi:
  - `GET /api/v1/chat/leads` (danh sách conversation có để lại SĐT/Email)
  - `GET /api/v1/chat/history/{conversation_id}` (lịch sử chat chi tiết)

---


## 3. Cấu trúc thư mục

### 3.1. Backend: `app/`

```text
app/
  __init__.py
  main.py

  api/
    v1/
      api.py
      endpoints/
        auth.py
        chat.py
        faq.py

  core/
    config.py
    database.py
    security.py

  crud/
    crud_chat.py
    crud_faq.py

  models/
    __init__.py
    conversation.py
    message.py
    user.py
    faq.py

  schemas/
    chat.py
    faq.py

  services/
    chatbot_engine.py
```

### 3.2. Frontend: `vnj-chatbot-fe/`

```text
vnj-chatbot-fe/
  index.html
  package.json
  vite.config.js
  public/

  src/
    App.jsx
    App.css
    main.jsx

    components/
      ChatBubble/
        index.jsx
      ChatWidget/
        index.jsx
        ChatWidget.css
      ChatWindow/
        ChatHeader.jsx
        ChatInput.jsx
        MessageList.jsx
        index.jsx

    pages/
      Admin/
        AdminLogin.jsx
        AdminDashboard.jsx

    services/
      api.js

    utils/
      helpers.js
```

---

## 4. Mô tả chi tiết Backend

### 4.1. `app/main.py`

**Nhiệm vụ:**
- `Base.metadata.create_all(bind=engine)` → tự tạo bảng nếu chưa có
- Seed **admin mặc định** vào bảng `users` nếu chưa tồn tại
- Cấu hình CORS
- Gắn router vào `/api/v1`

**Seed admin:**
- `username = "admin_vnj"`
- `password = "vnj@2026"` (được hash bằng bcrypt trước khi lưu)

**Lưu ý:** Cơ chế seed này chạy mỗi lần server khởi động (nhưng có kiểm tra `admin_exist`).

---

### 4.2. `app/core/config.py`

**Settings:**
- `DATABASE_URL` mặc định: `sqlite:///./chatbot_vnj.db`
- `SECRET_KEY` mặc định: `VNJ_SECRET_KEY_SIEUMAT_2026`
- `GROQ_API_KEY`: lấy từ biến môi trường `GROQ_API_KEY` (mặc định chuỗi rỗng)
- `ADMIN_DEFAULT_PASSWORD`: lấy từ biến môi trường `ADMIN_DEFAULT_PASSWORD` (mặc định `vnj@2026`)
- `ALGORITHM = "HS256"`


---

### 4.3. `app/core/database.py`

**Nhiệm vụ:**
- Khởi tạo `engine` từ `DATABASE_URL`
- `SessionLocal` để inject DB session vào các endpoint
- `get_db()` tạo/yield session rồi đóng sau request

---

### 4.4. `app/core/security.py`

- `verify_password()` dùng `passlib` bcrypt
- `get_password_hash()` để hash mật khẩu khi seed/tạo user
- `create_access_token()` tạo JWT với `exp` theo `ACCESS_TOKEN_EXPIRE_MINUTES`

---

### 4.5. `app/api/v1/api.py`

Gộp router:
- `/api/v1/chat` → `endpoints/chat.py`
- `/api/v1/faq` → `endpoints/faq.py`
- `/api/v1/auth` → `endpoints/auth.py`

---

## 5. API Chat (Public)

### 5.1. `app/api/v1/endpoints/chat.py`

#### POST `/api/v1/chat/start` → `start_chat`
- Tạo `Conversation` mới
- Trả về:
  - `session_id`
  - `message: "Phiên chat đã sẵn sàng."`

#### POST `/api/v1/chat/message` → `send_message`
Input: `session_id`, `message_text`

Flow:
1. Kiểm tra `Conversation` tồn tại
2. Trích SĐT/Email từ nội dung tin nhắn bằng regex
   - Nếu phát hiện được liên hệ và DB hiện chưa có `customer_phone` → cập nhật `customer_phone`
3. Lưu message user vào DB
4. Gọi `chatbot_engine.generate_bot_response(message_text, db, conversation_id=conv.id)`
5. Lưu message bot vào DB
6. Trả `MessageResponse`

#### GET `/api/v1/chat/leads`
- Lấy danh sách các `conversation` đã có `customer_phone`

#### GET `/api/v1/chat/history/{conversation_id}`
- Lấy toàn bộ lịch sử tin nhắn theo `conversation_id`

---


## 6. API Admin (Auth + FAQ)

### 6.1. `app/api/v1/endpoints/auth.py`

#### POST `/api/v1/auth/login`
- Nhận `OAuth2PasswordRequestForm` (username/password)
- Verify trong bảng `users`
- Nếu đúng → trả JWT:
  - `access_token`
  - `token_type = "bearer"`

---

### 6.2. `app/api/v1/endpoints/faq.py`

API đều require `current_user` từ JWT.

- POST `/api/v1/faq/`
- GET `/api/v1/faq/`
- PUT `/api/v1/faq/{faq_id}`
- DELETE `/api/v1/faq/{faq_id}`

Cơ chế xác thực:
- decode JWT bằng `settings.SECRET_KEY`
- lấy `sub` làm username
- kiểm tra user tồn tại trong DB

---

## 7. Service AI: `app/services/chatbot_engine.py`

### 7.1. Khởi tạo client Groq

```py
client = OpenAI(
  api_key=settings.GROQ_API_KEY,
  base_url="https://api.groq.com/openai/v1"
)
```

### 7.2. `generate_bot_response(message_text, db, conversation_id)`

#### (1) RAG dạng keyword match
- Lấy tất cả FAQ đang `is_active=True`
- Với mỗi FAQ:
  - `keywords` lấy bằng cách split theo dấu `,`
  - lowercase và check `kw in message_lower`
- Nếu match → append vào `context_text`

#### (2) Tạo prompt
- System prompt bắt chatbot trả lời ngắn 2-3 câu
- Nếu không có thông tin → prompt yêu cầu xin số điện thoại/điều hướng

#### (3) Lấy history hội thoại
- Nếu `conversation_id`:
  - query `Message` theo `conversation_id`
  - **(hiện tại trong code: `order_by(Message.id.desc()).limit(6)` và sau đó `reversed(history)` để giữ thứ tự thời gian)**


#### (4) Gọi LLM
- `model="llama-3.1-8b-instant"`
- `max_tokens=250`
- `temperature=0.2`

#### (5) Fallback khi lỗi
- trả câu thông báo “đường truyền đang bận…”

---

## 8. Models & Schema DB

### 8.1. `app/models/user.py` → `users`
- `id` PK
- `username` unique
- `hashed_password`
- `is_active`

### 8.2. `app/models/conversation.py` → `conversations`
- `id` PK
- `session_id` unique (UUID string)
- `customer_name`, `customer_phone`
- `status` default `active`

### 8.3. `app/models/message.py` → `messages`
- `id` PK
- `conversation_id` FK → `conversations.id`
- `sender` (string)
- `message_text`
- `created_at`

### 8.4. `app/models/faq.py` → `faq_knowledge_base`
- `category`
- `keywords` (string, kỳ vọng format: `keyword1, keyword2, ...`)
- `question_intent` (hiện chưa dùng trong RAG keyword match)
- `answer_text`
- `is_active`

---

## 9. CRUD layer

### `app/crud/crud_chat.py`
- `create_conversation()`
- `get_conversation_by_session()`
- `save_message()`
- `get_chat_history()` (hiện không dùng trực tiếp trong `chatbot_engine`)

### `app/crud/crud_faq.py`
- `create_faq()`
- `get_all_faqs()`
- `update_faq()` (dùng `model_dump(exclude_unset=True)`)
- `delete_faq()`

---

## 10. Mô tả chi tiết Frontend

### 10.1. `vnj-chatbot-fe/src/services/api.js`

- `API_BASE_URL = 'http://127.0.0.1:8000/api/v1'`
- axios interceptor:
  - nếu 401 → xóa token và redirect `/admin`

Endpoints:
- `chatAPI.startChat()` → POST `/chat/start`
- `chatAPI.sendMessage()` → POST `/chat/message`

Admin:
- login → POST `/auth/login` với form-urlencoded
- CRUD FAQ → `/faq/` + Authorization header

---

### 10.2. `ChatWidget`: `vnj-chatbot-fe/src/components/ChatWidget/index.jsx`

**UI/State:**
- `isOpen` (mở widget)
- `sessionId` (không có thì start chat)
- `messages[]` render thành ChatBubble/ChatWindow

**Flow:**
- Khi mở chat lần đầu → `startChat()` lấy `session_id`
- Khi gửi tin nhắn:
  - append message user vào UI
  - gọi `sendMessage(sessionId, text)`
  - append message bot bằng `botResponse.message_text || botResponse.text`

---

### 10.3. Admin pages

#### `AdminLogin.jsx`
- nhập username/password
- gọi `adminAPI.login`
- lưu JWT vào `localStorage` key: `vnj_admin_token`

#### `AdminDashboard.jsx`
- `fetchFAQs()` gọi `adminAPI.getFAQs()`
- hiển thị table + form thêm/sửa FAQ
- delete FAQ

---

## 11. Lỗi tiềm ẩn & lỗi hiện hữu (quan trọng)

### 11.1. Lỗi logic history hội thoại
Trong `chatbot_engine.generate_bot_response()`:
- code query:
  - `order_by(Message.id.asc()).limit(4)`
- nhưng comment nói “6 tin nhắn gần nhất” và biến history cần là tin nhắn gần nhất.

**Hậu quả:** prompt context bị lấy sai (tin nhắn cũ), làm bot phản hồi kém chất lượng.

---

### 11.2. RAG keyword match quá thô
- chỉ check `kw in message_lower`
- không normalize tốt, phụ thuộc cách admin nhập keywords
- không dùng `question_intent`

---

### 11.3. Potential mismatch role khi đổ history
- mapping role: `msg.sender == "user"` → user, còn lại assistant
- nếu sender stored khác giá trị chuẩn → vai trò role sai.

---

### 11.4. Cấu hình environment
- Frontend dùng API URL cố định `http://127.0.0.1:8000`
- Khi deploy production cần thay bằng env var.

---

## 12. Cách chạy dự án

---

## 12.0. Chạy bằng Docker (khuyến nghị)

### 12.0.1. Chuẩn bị
- Đảm bảo đã có Docker Desktop / Docker Engine.
- Tạo file `.env` ở thư mục gốc (nơi có `docker-compose.yml`).

> Các biến môi trường backend dùng trong Docker (theo code):
> - `GROQ_API_KEY` (**bắt buộc**)
> - `DATABASE_URL` (mặc định trong code: `sqlite:///./chatbot_vnj.db`)
> - `SECRET_KEY` (mặc định trong code)
> - `ADMIN_DEFAULT_PASSWORD` (mặc định trong code)

### 12.0.2. Chạy toàn bộ hệ thống
Trong thư mục gốc của project:

```bash
docker compose up --build -d
```

- Frontend (React) chạy tại: `http://localhost/` (Nginx trên port 80)
- Backend (FastAPI) chạy tại: `http://localhost:8000/api/v1`

### 12.0.3. Dừng hệ thống
```bash
docker compose down
```

---

## 12.1. macOS

### 12.1.1. Backend (BE - FastAPI)

#### Cài đặt phụ thuộc
```bash
cd "$(pwd)"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Chạy server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Backend sẽ tự tạo DB SQLite: `chatbot_vnj.db` (nếu chưa có)
- Admin mặc định sau khi chạy:
  - `username`: `admin_vnj`
  - `password`: `vnj@2026`

#### (Tuỳ chọn) Kiểm tra nhanh
- Mở trình duyệt: `http://127.0.0.1:8000/`
- Hoặc gọi một endpoint API để kiểm tra: `GET http://127.0.0.1:8000/api/v1/...`


---

### 12.1.2. Frontend (FE - React/Vite)

#### Cài đặt phụ thuộc
```bash
cd vnj-chatbot-fe
npm install
```

#### Chạy dev
```bash
npm run dev
```

- Mặc định FE chạy ở: `http://localhost:5173`
- FE đang trỏ API về: `http://127.0.0.1:8000/api/v1`

---

## 12.2. Windows

### 12.2.1. Backend (BE - FastAPI)

#### Cài đặt phụ thuộc
```bat
cd /d "%cd%"
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Chạy server
```bat
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Backend sẽ tự tạo DB SQLite: `chatbot_vnj.db` (nếu chưa có)
- Admin mặc định sau khi chạy:
  - `username`: `admin_vnj`
  - `password`: `vnj@2026`

---

### 12.2.2. Frontend (FE - React/Vite)

#### Cài đặt phụ thuộc
```bat
cd vnj-chatbot-fe
npm install
```

#### Chạy dev
```bat
npm run dev
```

- Mặc định FE chạy ở: `http://localhost:5173`

---

## 13. Hướng dẫn sử dụng nhanh (FE/BE)

### 13.1. Dùng Chatbot (Public)
1. Mở FE (React/Vite).
2. Mở widget chat và bắt đầu phiên.
3. Nhắn tin → FE gọi các API:
   - `POST /api/v1/chat/start`
   - `POST /api/v1/chat/message`

### 13.2. Đăng nhập Admin
- Trang admin trong FE: `/admin`
- Dùng tài khoản mặc định (sau khi BE đã chạy):
  - `admin_vnj` / `vnj@2026`

- Admin gọi các API bảo vệ bằng JWT trong header:
  - `Authorization: Bearer <token>`

### 13.3. Các endpoint Admin quan trọng
- `POST /api/v1/auth/login`
- `GET/POST/PUT/DELETE /api/v1/faq/`
- `GET /api/v1/chat/leads`
- `GET /api/v1/chat/history/{conversation_id}`

---

## 14. Thiết lập biến môi trường (Bắt buộc)

### 14.1. Backend (FastAPI)
Backend đọc `.env` tại thư mục gốc (file `.env` đặt cạnh `requirements.txt`).

Các biến quan trọng:
- `DATABASE_URL` (mặc định: `sqlite:///./chatbot_vnj.db`)
- `SECRET_KEY` (mặc định: `VNJ_SECRET_KEY_SIEUMAT_2026`)
- `GROQ_API_KEY` (**bắt buộc** để gọi Groq)
- `ADMIN_DEFAULT_PASSWORD` (mặc định: `vnj@2026`)

Ví dụ:
```bash
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_secret_key
ADMIN_DEFAULT_PASSWORD=your_admin_password
```

### 14.2. Frontend (React/Vite)
Frontend đọc base URL qua biến:
- `VITE_API_BASE_URL` (tuỳ chọn). Nếu không có, mặc định là `http://127.0.0.1:8000/api/v1`.

Ví dụ `.env` trong `vnj-chatbot-fe/`:
```bash
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```






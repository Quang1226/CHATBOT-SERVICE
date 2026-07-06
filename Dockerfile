# Sử dụng Python 3.12 siêu nhẹ làm nền tảng
FROM python:3.12-slim

# Chuyển thư mục làm việc vào /app
WORKDIR /app

# Copy file danh sách thư viện và cài đặt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn Backend vào thùng
COPY . .

# Mở cửa số 8000 để giao tiếp
EXPOSE 8000

# Lệnh khởi động Server khi thùng được chạy
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
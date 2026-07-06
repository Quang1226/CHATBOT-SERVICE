# --- GIAI ĐOẠN 1: Build mã nguồn React ---
FROM node:20-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# --- GIAI ĐOẠN 2: Chạy Web Server siêu nhẹ (Nginx) ---
FROM nginx:alpine
# Lấy các file tĩnh đã build từ giai đoạn 1 bỏ vào Nginx
COPY --from=build /app/dist /usr/share/nginx/html
# Copy file cấu hình điều hướng của Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
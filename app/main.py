from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base, SessionLocal
from app.models import conversation, message, faq, user as user_model
from app.core.security import get_password_hash
from app.api.v1.api import api_router

# Tự động tạo bảng nếu chưa có
Base.metadata.create_all(bind=engine)

# ĐOẠN CODE SEED DỮ LIỆU TÀI KHOẢN ADMIN MẶC ĐỊNH
db = SessionLocal()
try:
    admin_exist = db.query(user_model.User).filter(user_model.User.username == "admin_vnj").first()
    if not admin_exist:
        admin_user = user_model.User(
            username="admin_vnj",
            hashed_password=get_password_hash("vnj@2026"), # Mật khẩu đăng nhập
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print("=======> ĐÃ TẠO TÀI KHOẢN ADMIN MẶC ĐỊNH THÀNH CÔNG: admin_vnj / vnj@2026")
finally:
    db.close()

app = FastAPI(title="VNJ Chatbot API", version="1.0.0")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "https://www.vnj-ss.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Hệ thống Chatbot VNJ Backend bảo mật đang hoạt động!"}
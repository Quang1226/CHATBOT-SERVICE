import os

class Settings:
    PROJECT_NAME: str = "VNJ Chatbot API"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./chatbot_vnj.db")
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "VNJ_SECRET_KEY_SIEUMAT_2026") # Chuỗi mã hóa bí mật
    GROQ_API_KEY: str = "GROQ_API_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # Token có hiệu lực trong 24 giờ

settings = Settings()
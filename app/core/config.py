import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = "VNJ Chatbot API"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./chatbot_vnj.db")
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "VNJ_SECRET_KEY_SIEUMAT_2026") 
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    ADMIN_DEFAULT_PASSWORD: str = os.getenv("ADMIN_DEFAULT_PASSWORD", "vnj@2026")
    
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # Token có hiệu lực trong 24 giờ

settings = Settings()
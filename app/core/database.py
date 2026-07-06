from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Tạo engine SQLAlchemy dựa trên kiểu CSDL trong DATABASE_URL.
# - SQLite: cần connect_args để tắt kiểm tra thread (check_same_thread=False)
# - PostgreSQL/khác: dùng mặc định
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(settings.DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
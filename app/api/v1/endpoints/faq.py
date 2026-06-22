from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from jose import jwt, JWTError

from app.core.database import get_db
from app.core.config import settings
from app.schemas import faq as faq_schema
from app.crud import crud_faq
from app.models.user import User

router = APIRouter()

# Khai báo đường dẫn lấy Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Hàm gác cổng: Giải mã Token để nhận diện Admin, nếu sai hoặc hết hạn sẽ chặn đứng lại"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Phiên đăng nhập đã hết hạn hoặc không hợp lệ",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


# ÁP DỤNG Ổ KHÓA VÀO CÁC API
@router.post("/", response_model=faq_schema.FAQResponse)
def create_new_faq(
    faq: faq_schema.FAQCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # <-- Thêm dòng này để khóa API lại
):
    """API dành cho Admin: Thêm câu hỏi mới (Yêu cầu đăng nhập)"""
    return crud_faq.create_faq(db, faq)

@router.get("/", response_model=List[faq_schema.FAQResponse])
def read_all_faqs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # <-- Thêm dòng này để khóa API lại
):
    """API dành cho Admin: Xem danh sách FAQ (Yêu cầu đăng nhập)"""
    return crud_faq.get_all_faqs(db)

@router.put("/{faq_id}", response_model=faq_schema.FAQResponse)
def update_existing_faq(
    faq_id: int, 
    faq_in: faq_schema.FAQUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Khóa bảo mật
):
    """API dành cho Admin: Sửa nội dung một FAQ đã có"""
    updated_faq = crud_faq.update_faq(db=db, faq_id=faq_id, faq_in=faq_in)
    if not updated_faq:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi này trong hệ thống")
    return updated_faq

@router.delete("/{faq_id}")
def delete_existing_faq(
    faq_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Khóa bảo mật
):
    """API dành cho Admin: Xóa một FAQ khỏi hệ thống"""
    success = crud_faq.delete_faq(db=db, faq_id=faq_id)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi này trong hệ thống")
    return {"message": "Đã xóa thành công!"}
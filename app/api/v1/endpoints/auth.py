from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core import security
from app.models.user import User

router = APIRouter()

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Xác thực tài khoản Admin và trả về JWT Token để Frontend lưu trữ.

    API này nhận username/password thông qua OAuth2PasswordRequestForm.
    """
    # 1) Tìm user trong DB theo username
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản hoặc mật khẩu không chính xác"
        )
    
    # 2. Kiểm tra mật khẩu
    if not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản hoặc mật khẩu không chính xác"
        )
        
    # 3. Tạo token trả về cho Frontend lưu trữ
    access_token = security.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Khi khách hàng bắt đầu phiên chat mới
class ChatStartRequest(BaseModel):
    customer_name: Optional[str] = "Khách hàng ẩn danh"
    customer_phone: Optional[str] = None

# Khi tạo phiên chat thành công
class ChatStartResponse(BaseModel):
    session_id: str
    message: str

# Khi khách hàng gửi 1 tin nhắn
class MessageCreate(BaseModel):
    session_id: str
    message_text: str

# Khi khách hàng nhận tin nhắn từ hệ thống
class MessageResponse(BaseModel):
    sender: str
    message_text: str
    created_at: datetime

    class Config:
        from_attributes = True 
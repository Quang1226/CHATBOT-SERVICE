import re
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import chat as chat_schema
from app.crud import crud_chat
from app.services import chatbot_engine
from app.core.limiter import limiter

router = APIRouter()

@router.post("/start", response_model=chat_schema.ChatStartResponse)
def start_chat(request: chat_schema.ChatStartRequest, db: Session = Depends(get_db)):
    """Khởi tạo một phiên chat mới"""
    conv = crud_chat.create_conversation(db, request.customer_name, request.customer_phone)
    return {"session_id": conv.session_id, "message": "Phiên chat đã sẵn sàng."}

@router.post("/message", response_model=chat_schema.MessageResponse)
@limiter.limit("20/minute")  # Giới hạn 20 request/phút theo IP để chống spam
async def send_message(
    request: Request,
    payload: chat_schema.MessageCreate, 
    db: Session = Depends(get_db)
):
    """Nhận tin nhắn từ khách hàng và trả về phản hồi của chatbot.

    Quy trình chính:
    - Kiểm tra session có tồn tại
    - Trích xuất SĐT/Email từ nội dung tin nhắn (nếu có)
    - Lưu tin nhắn user và gọi chatbot_engine để tạo phản hồi
    - Lưu tin nhắn bot và trả về cho frontend
    """
    # 1) Kiểm tra phiên chat có tồn tại không

    conv = crud_chat.get_conversation_by_session(db, payload.session_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Session không tồn tại")
    
    phone_pattern = r"(0[3|5|7|8|9]|84[3|5|7|8|9])([0-9]{8})\b"
    phone_match = re.search(phone_pattern, payload.message_text)
    
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    email_match = re.search(email_pattern, payload.message_text)
    
    contact_info = []
    if phone_match: contact_info.append(phone_match.group(0))
    if email_match: contact_info.append(email_match.group(0))
    
    if contact_info and not conv.customer_phone:
        conv.customer_phone = " / ".join(contact_info)
        conv.status = "HOT"
        db.commit()
    
    # 2. Lưu tin nhắn của Khách hàng vào DB
    crud_chat.save_message(db, conv.id, sender="user", text=payload.message_text)
    
    # 3. Đưa tin nhắn vào bộ não Chatbot để lấy câu trả lời
    bot_reply_text = await chatbot_engine.generate_bot_response(
        message_text=payload.message_text, 
        db=db,
        conversation_id=conv.id
    )

    # 4. Lưu câu trả lời của Bot vào DB
    bot_msg = crud_chat.save_message(db, conv.id, sender="bot", text=bot_reply_text)
    
    return bot_msg

@router.get("/leads")
def get_leads_list(db: Session = Depends(get_db)):
    """API lấy danh sách khách hàng tiềm năng"""
    return crud_chat.get_all_leads(db)

@router.get("/history/{conversation_id}")
def get_conversation_history(conversation_id: int, db: Session = Depends(get_db)):
    """API lấy chi tiết lịch sử tin nhắn của một phiên chat"""
    return crud_chat.get_chat_history(db, conversation_id)
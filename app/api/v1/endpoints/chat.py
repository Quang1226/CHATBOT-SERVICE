import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import chat as chat_schema
from app.crud import crud_chat
from app.services import chatbot_engine

router = APIRouter()

@router.post("/start", response_model=chat_schema.ChatStartResponse)
def start_chat(request: chat_schema.ChatStartRequest, db: Session = Depends(get_db)):
    """Khởi tạo một phiên chat mới"""
    conv = crud_chat.create_conversation(db, request.customer_name, request.customer_phone)
    return {"session_id": conv.session_id, "message": "Phiên chat đã sẵn sàng."}

@router.post("/message", response_model=chat_schema.MessageResponse)
def send_message(request: chat_schema.MessageCreate, db: Session = Depends(get_db)):
    """Xử lý tin nhắn khách hàng gửi lên và trả về câu trả lời của Bot"""
    # 1. Kiểm tra phiên chat có tồn tại không
    conv = crud_chat.get_conversation_by_session(db, request.session_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Session không tồn tại")
    
    phone_pattern = r"(0[3|5|7|8|9]|84[3|5|7|8|9])([0-9]{8})\b"
    phone_match = re.search(phone_pattern, request.message_text)
    
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    email_match = re.search(email_pattern, request.message_text)
    
    contact_info = []
    if phone_match: contact_info.append(phone_match.group(0))
    if email_match: contact_info.append(email_match.group(0))
    
    if contact_info and not conv.customer_phone:
        # Lưu số điện thoại hoặc email (hoặc cả hai) vào DB
        conv.customer_phone = " / ".join(contact_info)
        db.commit()
    
    # 2. Lưu tin nhắn của Khách hàng vào DB
    crud_chat.save_message(db, conv.id, sender="user", text=request.message_text)
    
    # 3. Đưa tin nhắn vào bộ não Chatbot để lấy câu trả lời
    bot_reply_text = chatbot_engine.generate_bot_response(
        message_text=request.message_text, 
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
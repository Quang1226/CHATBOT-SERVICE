from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.models.message import Message
import uuid

def create_conversation(db: Session, name: str, phone: str):
    # Sinh ra mã ngẫu nhiên và duy nhất cho phiên chat
    new_session_id = str(uuid.uuid4()) 
    db_conv = Conversation(
        session_id=new_session_id,
        customer_name=name,
        customer_phone=phone
    )
    db.add(db_conv)
    db.commit()
    db.refresh(db_conv)
    return db_conv

def get_conversation_by_session(db: Session, session_id: str):
    return db.query(Conversation).filter(Conversation.session_id == session_id).first()

def save_message(db: Session, conversation_id: int, sender: str, text: str):
    db_msg = Message(
        conversation_id=conversation_id,
        sender=sender,
        message_text=text
    )
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return db_msg

def get_chat_history(db: Session, conversation_id: int):
    return db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()

def get_all_leads(db: Session):
    """Lấy danh sách các phiên chat CÓ chứa số điện thoại hoặc email, xếp mới nhất lên đầu"""
    return db.query(Conversation).filter(Conversation.customer_phone.isnot(None)).order_by(Conversation.id.desc()).all()
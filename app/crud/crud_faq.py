from sqlalchemy.orm import Session
from app.models.faq import FAQ
from app.schemas import faq as faq_schema

def create_faq(db: Session, faq: faq_schema.FAQCreate):
    """Thêm một câu hỏi/trả lời FAQ mới vào Cơ sở dữ liệu"""
    db_faq = FAQ(
        category=faq.category,
        keywords=faq.keywords,
        question_intent=faq.question_intent,
        answer_text=faq.answer_text,
        is_active=faq.is_active
    )
    db.add(db_faq)
    db.commit()
    db.refresh(db_faq)
    return db_faq

def get_all_faqs(db: Session):
    """Lấy toàn bộ danh sách FAQ có trong hệ thống"""
    return db.query(FAQ).all()

def update_faq(db: Session, faq_id: int, faq_in: faq_schema.FAQUpdate):
    """Cập nhật nội dung của một câu hỏi FAQ đã tồn tại"""
    # 1. Tìm câu hỏi dựa trên ID
    db_faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not db_faq:
        return None
    
    # 2. Lọc ra các trường được Admin gửi lên để cập nhật (trường nào không gửi sẽ giữ nguyên)
    update_data = faq_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_faq, key, value)
        
    # 3. Lưu thay đổi vào Cơ sở dữ liệu
    db.commit()
    db.refresh(db_faq)
    return db_faq

def delete_faq(db: Session, faq_id: int):
    """Xóa hoàn toàn một câu hỏi FAQ khỏi hệ thống"""
    # 1. Tìm câu hỏi dựa trên ID
    db_faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not db_faq:
        return False
        
    # 2. Thực hiện lệnh xóa
    db.delete(db_faq)
    db.commit()
    return True
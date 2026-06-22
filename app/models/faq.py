from sqlalchemy import Column, Integer, String, Text, Boolean
from app.core.database import Base

class FAQ(Base):
    __tablename__ = "faq_knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), index=True)
    keywords = Column(String(255))
    question_intent = Column(String(255))
    answer_text = Column(Text)
    is_active = Column(Boolean, default=True)
from pydantic import BaseModel
from typing import Optional

class FAQBase(BaseModel):
    category: str
    keywords: str
    question_intent: str
    answer_text: str
    is_active: Optional[bool] = True

class FAQCreate(FAQBase):
    pass

class FAQResponse(FAQBase):
    id: int

    class Config:
        from_attributes = True
        
class FAQUpdate(BaseModel):
    category: Optional[str] = None
    keywords: Optional[str] = None
    question_intent: Optional[str] = None
    answer_text: Optional[str] = None
    is_active: Optional[bool] = None
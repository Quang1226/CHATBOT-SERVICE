from openai import OpenAI
from app.core.config import settings
from app.models.faq import FAQ
from app.models.message import Message # <-- Thêm dòng import này
from sqlalchemy.orm import Session

client = OpenAI(
    api_key=settings.GROQ_API_KEY, 
    base_url="https://api.groq.com/openai/v1"
)

def generate_bot_response(message_text: str, db: Session, conversation_id: int = None) -> str:
    # 1. TRUY XUẤT RAG (Lấy dữ liệu từ bảng điều khiển Admin)
    faqs = db.query(FAQ).filter(FAQ.is_active == True).all()
    context_text = ""
    message_lower = message_text.lower()
    for faq in faqs:
        keywords = [k.strip().lower() for k in faq.keywords.split(',')]
        if any(kw in message_lower for kw in keywords):
            context_text += f"- Danh mục {faq.category}: {faq.answer_text}\n"

    # 2. CHỈ THỊ MẬT (PROMPT)
    system_prompt = f"""Bạn là nhân viên Chăm sóc khách hàng của công ty công nghệ VNJ. 
    VNJ CHỈ kinh doanh 4 dịch vụ: Phát triển Website, Phát triển Phần mềm/App, Hệ thống môi trường (IoT), và Ứng dụng Mobile.
    QUY TẮC BẮT BUỘC:
    1. TRẢ LỜI CỰC KỲ NGẮN GỌN (tối đa 2-3 câu). TUYỆT ĐỐI KHÔNG liệt kê dài dòng.
    2. Nếu khách hàng hỏi chung chung, hãy chào mừng và HỎI NGƯỢC LẠI 1 câu ngắn gọn để khai thác nhu cầu.
    3. Dựa vào [CƠ SỞ TRI THỨC] để tư vấn. Nếu không có thông tin, hãy xin số điện thoại để chuyên viên gọi lại.
    4. Xưng "em" và gọi khách là "anh/chị".
    5. KHÔNG được tự ý thêm thông tin ngoài [CƠ SỞ TRI THỨC].
    6. Không được hỏi về các vấn đề ngoài lĩnh vực CSKH, hãy trả lời: "Xin lỗi anh/chị, em không thể tư vấn về vấn đề này. Anh/chị vui lòng liên hệ trực tiếp với chuyên viên để được hỗ trợ nhé!"
    7. QUY TRÌNH XIN THÔNG TIN: > - TUYỆT ĐỐI KHÔNG được nói "Em sẽ liên hệ lại" hoặc "Cảm ơn anh/chị đã cung cấp" nếu khách hàng CHƯA ghi ra số điện thoại hoặc email.
        Nếu khách đồng ý tư vấn nhưng chưa cho số, BẮT BUỘC phải hỏi: "Dạ anh/chị cho em xin tên và số điện thoại (hoặc email) để chuyên viên VNJ gọi điện hỗ trợ chi tiết hơn cho mình nhé."
    
    [CƠ SỞ TRI THỨC]:
    {context_text if context_text else "Không có thông tin."}
    """

    # 3. NẠP TRÍ NHỚ TỪ DATABASE
    api_messages = [{"role": "system", "content": system_prompt}]
    
    if conversation_id:
        history = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.id.desc()).limit(6).all()
        
        for msg in reversed(history):
            role = "user" if msg.sender == "user" else "assistant"
            api_messages.append({"role": role, "content": msg.message_text})
    else:
        api_messages.append({"role": "user", "content": message_text})

    # 4. GỌI GROQ
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=api_messages,
            max_tokens=250,
            temperature=0.2 
        )
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Lỗi khi gọi Groq API: {e}")
        return "Xin lỗi anh/chị, đường truyền kết nối máy chủ đang bận. Anh/chị vui lòng thử lại sau giây lát nhé!"
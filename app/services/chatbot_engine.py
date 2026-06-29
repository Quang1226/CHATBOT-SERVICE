import re
import logging
from openai import OpenAI
from app.core.config import settings
from app.models.faq import FAQ
from app.models.message import Message 
from sqlalchemy.orm import Session

# ================= CẤU HÌNH LOGGING =================
# Thiết lập bộ quan sát hệ thống (In ra Console với format chuyên nghiệp)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)
# ====================================================

client = OpenAI(
    api_key=settings.GROQ_API_KEY, 
    base_url="https://api.groq.com/openai/v1"
)

def generate_bot_response(message_text: str, db: Session, conversation_id: int = None) -> str:
    # 1. TRUY XUẤT RAG (ĐÃ NÂNG CẤP THUẬT TOÁN TÌM KIẾM CHÍNH XÁC)
    logger.info(f"Đang xử lý tin nhắn: '{message_text}' cho Session ID: {conversation_id}")
    
    faqs = db.query(FAQ).filter(FAQ.is_active == True).all()
    context_text = ""
    matched_categories = []
    
    for faq in faqs:
        keywords = [k.strip() for k in faq.keywords.split(',')]
        
        # Duyệt qua từng từ khóa, dùng Regex để bắt CHÍNH XÁC từ (không bắt từ chứa chuỗi con)
        for kw in keywords:
            if not kw: continue
            
            # (?:^|\W) đảm bảo đằng trước là đầu câu hoặc khoảng trắng/dấu câu
            # (?:$|\W) đảm bảo đằng sau là cuối câu hoặc khoảng trắng/dấu câu
            # (?i) là không phân biệt hoa thường
            pattern = rf"(?i)(?:^|\W){re.escape(kw)}(?:$|\W)"
            
            if re.search(pattern, message_text):
                context_text += f"- {faq.category}: {faq.answer_text}\n"
                matched_categories.append(faq.category)
                break # Tìm thấy 1 từ khóa là đủ để lấy FAQ này, thoát vòng lặp con
                
    # Ghi log kết quả RAG để Admin dễ dàng debug
    if matched_categories:
        logger.info(f"RAG tìm thấy ngữ cảnh từ danh mục: {', '.join(matched_categories)}")
    else:
        logger.info("RAG không tìm thấy FAQ phù hợp. AI sẽ tự trả lời.")

    # 2. CHỈ THỊ MẬT (PROMPT) - Giữ nguyên bộ luật thép
    system_prompt = f"""Bạn là Chuyên viên Tư vấn công nghệ của VNJ.
    VNJ CHỈ làm: Web, App, Phần mềm, IoT.
    
    QUY TẮC SỐNG CÒN (VI PHẠM SẼ BỊ PHẠT):
    1. XƯNG HÔ THÔNG MINH: Luôn xưng "em". BẮT BUỘC QUÉT TỪ NGỮ CỦA KHÁCH: Nếu khách tự xưng là "anh", "chị", "tôi", "chú", "cô"... thì BẮT BUỘC phải gọi khách bằng danh xưng tương ứng. CHỈ DÙNG "anh/chị" khi khách nói trống không (Ví dụ: "xin chào", "tư vấn cho mình").
    2. CẤM LẠC ĐỀ (RẤT QUAN TRỌNG): NẾU khách hỏi chủ đề KHÔNG thuộc lĩnh vực công nghệ (như học toán, nấu ăn, chính trị, thời tiết...), TUYỆT ĐỐI KHÔNG giải thích dông dài. CHỈ ĐƯỢC TRẢ LỜI ĐÚNG 1 CÂU DUY NHẤT: "Dạ VNJ là công ty công nghệ nên em chỉ hỗ trợ tư vấn về phần mềm/web/app thôi ạ. Rất mong [danh_xưng_của_khách] thông cảm!"
    3. CẤM BÁO GIÁ: Tuyệt đối không đưa ra con số báo giá. Hãy báo chuyên viên sẽ liên hệ để báo giá chính xác.
    4. CẤM LẢM NHẢM: Không giải thích nội tâm, không dùng ký tự sao (*). Dùng dấu gạch ngang (-) để liệt kê.
    5. XỬ LÝ SAU KHI CÓ SĐT: Nếu khách đã cho SĐT/Email, CHỈ CẦN cảm ơn ngắn gọn và báo chuyên viên sẽ liên hệ. TUYỆT ĐỐI KHÔNG nhại lại thông tin (Tên:..., SĐT:...).
    
    [ĐÁNH GIÁ KHÁCH HÀNG TIỀM NĂNG]:
    Nếu khách ĐÃ ĐỂ LẠI Số điện thoại/Email, BẮT BUỘC chèn đúng chữ HOT_LEAD vào cuối cùng của câu trả lời.
    
    [CƠ SỞ TRI THỨC VNJ]:
    {context_text if context_text else "Hãy tư vấn dựa trên kiến thức công nghệ chung."}
    """

    # 3. NẠP TRÍ NHỚ TỪ DATABASE
    api_messages = [{"role": "system", "content": system_prompt}]
    
    if conversation_id:
        history = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.id.desc()).limit(20).all()
        for msg in reversed(history):
            role = "user" if msg.sender == "user" else "assistant"
            api_messages.append({"role": role, "content": msg.message_text})
    else:
        api_messages.append({"role": "user", "content": message_text})

    # 4. GỌI GROQ CÓ BẮT LỖI LOGGING
    try:
        logger.info("Đang gửi Request tới bộ não Groq AI...")
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=api_messages,
            max_tokens=600, 
            temperature=0.3
        )
        bot_reply = response.choices[0].message.content
        logger.info("Groq AI trả lời thành công.")
        return bot_reply
        
    except Exception as e:
        # Ghi log màu đỏ rực kèm theo đường dẫn lỗi chi tiết (Traceback)
        logger.error(f"LỖI NGHIÊM TRỌNG KHI GỌI GROQ API: {str(e)}", exc_info=True)
        return "Xin lỗi anh/chị, hệ thống đang bận chút xíu. Anh/chị vui lòng thử lại sau giây lát nhé!"
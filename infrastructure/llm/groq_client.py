# infrastructure/llm/groq_client.py

from openai import OpenAI
import os

class GroqClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )

    def chat(self, prompt: str):
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
        )

        return response.choices[0].message.content
    
    
    def generate_answer(self, question: str, context: str) -> str:
        prompt = f"""
    Bạn là trợ lý pháp lý AI chuyên về pháp luật thuế Việt Nam.

    NHIỆM VỤ:
    - Chỉ trả lời dựa trên CONTEXT được cung cấp.
    - Không tự suy diễn hoặc bịa thêm quy định pháp luật.
    - Nếu context không đủ, hãy nói rõ:
    "Tôi không có đủ thông tin trong dữ liệu hiện tại để trả lời chính xác câu hỏi này."

    QUY TẮC TRẢ LỜI:
    1. Ưu tiên trích dẫn:
    - Điều
    - Khoản
    - Điểm
    nếu có trong context.

    2. Nếu câu hỏi yêu cầu:
    - điều kiện
    - trường hợp
    - nghĩa vụ
    - thủ tục
    - mức xử lý
    thì hãy liệt kê rõ từng ý theo bullet points.

    3. Không được:
    - đưa ra lời khuyên pháp lý cá nhân
    - khẳng định điều không có trong context
    - suy diễn luật ngoài context

    4. Nếu có nhiều điều luật liên quan:
    - hãy tóm tắt theo thứ tự logic
    - ưu tiên điều luật trực tiếp liên quan nhất

    5. Nếu context chứa nhiều phiên bản/nội dung tương tự:
    - ưu tiên nội dung khớp nhất với câu hỏi.

    6. Khi trả lời:
    - ưu tiên mở đầu bằng căn cứ pháp lý, ví dụ:
    "Căn cứ Khoản ... Điều ... của ..."
    hoặc
    "Theo Điều ... của ..."
    - nếu có đủ Điều/Khoản/Điểm trong context thì phải nêu đầy đủ.

    7. Cách trình bày:
    - Trả lời ngắn gọn trước.
    - Sau đó mới giải thích chi tiết nếu cần.
    - Không sao chép toàn bộ context.
    - Chỉ tóm tắt đúng nội dung pháp lý quan trọng nhất.

    8. Nếu câu hỏi yêu cầu liệt kê:
    - dùng bullet points.
    - giữ nguyên ký hiệu a), b), c), đ), e) nếu context có.

    9. Nếu context có nhiều nguồn:
    - ưu tiên nguồn trực tiếp nhất với câu hỏi.
    - không đưa nguồn phụ vào câu trả lời nếu không cần thiết.

    10. Phân loại nguồn pháp lý:
    - "Căn cứ trực tiếp": điều/khoản/điểm trả lời thẳng vào câu hỏi.
    - "Nguồn liên quan": điều/khoản/điểm chỉ bổ sung, giải thích hoặc liên hệ.
    - Khi trả lời, luôn ưu tiên căn cứ trực tiếp trước.
    - Không biến nguồn liên quan thành căn cứ chính.
    - Nếu dùng nguồn liên quan, hãy ghi rõ: "Ngoài ra, nguồn liên quan..."

    QUESTION:
    {question}

    CONTEXT:
    {context}

    TRẢ LỜI:
    """.strip()

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
        )

        return response.choices[0].message.content.strip()
import os
import re
from openai import OpenAI
import json
from typing import List, Dict, Any, Tuple
from ..models.chat_history_model import Message
from app.database import get_chat_history_collection
import logging

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
assistant_id = os.getenv("OPENAI_ASSISTANT_ID")


def _strip_emojis(text: str) -> str:
    """Remove common emoji/pictographic Unicode characters from text."""
    if not text:
        return text
    try:
        emoji_pattern = re.compile(
            u"[" 
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
            u"\U00002700-\U000027BF"  # dingbats
            u"\U0001F900-\U0001F9FF"  # supplemental symbols
            u"\U00002600-\U000026FF"  # misc symbols
            u"\U00002B00-\U00002BFF"  # arrows, etc
            u"]+",
            flags=re.UNICODE)
        return emoji_pattern.sub(r"", text)
    except re.error:
        # fallback: remove a few common glyphs
        return re.sub(r"[\u2600-\u26FF\u2700-\u27BF]", "", text)

async def process_message_with_assistant_tool(
    message: str,
    session_id: str = None,
    n_history: int = 5,
    enhance_response: bool = True
) -> Tuple[str, dict]:
    """
    Process user message using OpenAI Assistant tool with vector search and chat history context.
    Returns: (AI's answer, token_usage dict from .usage field if available, else zeros)
    Includes automatic enhancement with OpenAI for better formatting.
    """
    logger.info(f"Processing message with enhance_response={enhance_response}")
    # Collect chat history
    chat_history = []
    if session_id:
        collection = get_chat_history_collection()
        session_data = collection.find_one({"session_id": session_id})
        if session_data:
            chat_history = session_data.get("messages", [])

    # Prepare messages for context (last n_history + current)
    messages = []
    if chat_history:
        for msg in chat_history[-n_history:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    try:
        # Call OpenAI Assistant API (threading for context)
        thread = client.beta.threads.create(messages=messages)
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
        # Ensure token_usage is always defined so we can safely return it later
        token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        # Wait for completion (polling)
        import time
        while run.status not in ("completed", "failed", "cancelled"):
            time.sleep(0.5)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run.status == "completed":
            # Get the latest message from the thread
            thread_messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
            assistant_reply = None
            if thread_messages and len(thread_messages) > 0:
                assistant_reply = thread_messages[0].content[0].text.value
            if assistant_reply is None:
                return ("[No assistant reply found.]", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})

            # Filter and format the response
            # assistant_reply = filter_response(assistant_reply)  # Removed filter function
            logger.info(f"Response after local filtering: {len(assistant_reply)} chars")
            
            # Send to OpenAI for final enhancement
            if enhance_response:
                logger.info("Starting OpenAI enhancement...")
                try:
                    enhanced_reply = await enhance_with_openai(assistant_reply, message)
                    if enhanced_reply:
                        logger.info(f"Enhancement successful: {len(enhanced_reply)} chars")
                        # Ensure no emojis are returned
                        enhanced_reply = _strip_emojis(enhanced_reply)
                        assistant_reply = enhanced_reply
                    else:
                        logger.warning("Enhancement returned empty result")
                except Exception as e:
                    logger.error(f"Enhancement failed: {e}")
                    # Continue with filtered response
            else:
                logger.info("Enhancement disabled, using filtered response only")

            # Try to get token usage from .usage field if available
            
            if hasattr(run, "usage") and run.usage:
                usage = run.usage
                token_usage = {
                    "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(usage, "completion_tokens", 0),
                    "total_tokens": getattr(usage, "total_tokens", 0)
                }

            # strip emojis from final assistant reply as an extra safety
            assistant_reply = _strip_emojis(assistant_reply)
            return assistant_reply, token_usage
        else:
            logger.error(f"Assistant run failed: {run.status}")
            return ("[Assistant failed to generate a response.]", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})
    except Exception as e:
        logger.error(f"OpenAI Assistant API error: {e}")
        return ("[Error communicating with Assistant API.]", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})

async def enhance_with_openai(raw_response: str, original_message: str) -> str:
    """
    Send the raw response to OpenAI for final enhancement and formatting.
    """
    try:
        enhancement_prompt = f"""Đây là phản hồi từ trợ lý AI cho câu hỏi: "{original_message}"
Phản hồi gốc: {raw_response} Vai trò & phong cách: Bạn là một "nhà tư vấn bán hàng có tâm" — thân thiện, trung thực, thực tế và nhiệt tình. Trả lời như một người tư vấn trực tiếp cho khách: dùng ngôi xưng thân mật (ví dụ "Mình"), ngắn gọn, dễ đọc, không khoa trương. Yêu cầu cải thiện (trả về bằng tiếng Việt, tự nhiên và không giống robot): 1) Giữ định dạng rõ ràng: xuống dòng để tách phần, dùng **text** để in đậm tiêu đề sản phẩm. 2) Tuyệt đối KHÔNG TẠO hoặc BÁN CÁC liên kết/giá giả. Chỉ chèn liên kết nếu phản hồi gốc có URL thực; nếu không có URL, bỏ luôn mục "Nơi mua". Nếu có link thực, ẩn link bên trong tên nền tảng bằng cú pháp markdown, ví dụ [Shopee](https://...), [Drive](https://...). 3) KHÔNG THÊM emoji/biểu tượng dưới bất kỳ hình thức nào trong toàn bộ phản hồi. Tuyệt đối không chèn bất kỳ ký tự cảm xúc hoặc biểu tượng nào. 4) Thay vì một mục riêng "Nhận định của tôi", hãy khéo léo xen 1 câu nhận xét tinh tế ngay trong mô tả sản phẩm (ví dụ: "Mình thấy sản phẩm này phù hợp cho gia đình có trẻ nhỏ vì..."). Giữ nhận xét ngắn, thực tế và có tính đề xuất (ví dụ "phù hợp nếu...", "tốt cho..."). 5) Nếu có giá/ưu đãi trong phản hồi gốc, đặt vào mục "Giá & Ưu đãi"; không đoán giá nếu không có dữ liệu. 6) Nếu phản hồi gốc có link rút gọn hoặc link đến Drive/TikTok/Facebook/Shopee, hiển thị dưới dạng markdown link với tên nền tảng (ví dụ [Drive](...)). 7) Tránh bảng, JSON hay metadata; viết như một người tư vấn: thân thiện, ngắn, rõ ràng. Kết quả mong muốn (chỉ trả về phần văn bản đã định dạng, không giải thích cách làm): - Tiêu đề sản phẩm (in đậm bằng ** ) - Các thuộc tính chính (dung tích, công dụng, đặc điểm nổi bật,...), mỗi dòng 1 ý - Giá & Ưu đãi (nếu phản hồi gốc có) - Nơi mua (nếu phản hồi gốc có link) với markdown links Phong cách cụ thể: thân mật, nhẹ nhàng, trung thực; tránh xưng quá trang trọng hoặc quá kỹ thuật. Khi cần gợi ý, dùng câu như "Mình khuyên..." hoặc "Nếu bạn cần...". YÊU CẦU MỞ RỘNG (bắt buộc): - Với mỗi sản phẩm, liệt kê CHI TIẾT tất cả tính năng / đặc tính có trong phản hồi gốc và nếu có thể suy luận một cách hợp lý từ dữ liệu: thành phần, công nghệ (nếu có), khả năng tẩy/rửa, khử mùi, độ an toàn cho da, cấp độ hương thơm, hiệu quả tiết kiệm/người dùng, dạng (lỏng/túi/bọt), dung tích, hướng dẫn sử dụng (liều lượng cho kg quần áo), lưu ý an toàn (tránh tiếp xúc với mắt, v.v.), cách bảo quản, và đối tượng khuyên dùng. - Nếu phản hồi gốc KHÔNG CUNG CẤP thông tin nào trong các mục trên, hãy BỎ QUA mục đó (không in "Không có thông tin" và không tự bịa thông tin). - Ở cuối mỗi sản phẩm, thêm 1 mục nhỏ "Mẹo ngắn" (1 câu) gợi ý bảo quản hoặc cách dùng để hiệu quả hơn, nếu có thể. - Giữ phong cách tư vấn: xen 1 câu nhận xét tinh tế trong mô tả (không cần mục riêng), ví dụ "Mình nghĩ sản phẩm này phù hợp cho...". - Không thêm liên kết hoặc giá nếu không có trong phản hồi gốc; nếu có link, dùng markdown link với tên nền tảng. Trả về chỉ phần văn bản đã định dạng, đầy đủ chi tiết theo yêu cầu trên.
"""

        # Create a simple chat completion for enhancement
        response = client.chat.completions.create(
            model="gpt-4.1",  # Use cheaper model for enhancement
            messages=[
                {"role": "system", "content": "Bạn là một chuyên gia định dạng và cải thiện phản hồi chatbot. Hãy làm cho phản hồi trở nên đẹp mắt và chuyên nghiệp hơn."},
                {"role": "user", "content": enhancement_prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        enhanced_response = response.choices[0].message.content.strip()
        return enhanced_response
        
    except Exception as e:
        logger.error(f"Error enhancing response with OpenAI: {e}")
        # Return raw response if enhancement fails
        return raw_response

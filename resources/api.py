
import requests
from langdetect import detect
from languages import LANGUAGES

#  Thay API_KEY này bằng khóa thật của bạn (từ Google AI Studio)
API_KEY = "AIzaSyD62h3zdvXMrhK2TcptJd1RLgBPNM7IhQw"

#  Dùng model ổn định nhất hiện nay
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


CONTEXTS = [
    "Daily", "Medical/Healthcare", "Technical/IT", "Legal/Contracts",
    "Business/Work", "Study/Education", "Slang", "Idiom"
]

LANGUAGES = []

def translate_text(text, src_lang="auto", dst_lang="vi", domain="General") -> str:
    if not text.strip():
        return ""
# Tự động nhận dạng ngôn ngữ nếu người chọn "auto"
    if src_lang.lower() == "auto":
        try:
            detected = detect(text)
            # Mapping từ code ngắn sang tên đầy đủ để Gemini hiểu chính xác
            lang_mapping = {
                "en": "English",
                "vi": "Vietnamese", 
                "zh": "Chinese",
                "ja": "Japanese",
                "ko": "Korean",
                "fr": "French",
                "de": "German",
                "es": "Spanish",
                "it": "Italian",
                "pt": "Portuguese",
                "ru": "Russian",
                "ar": "Arabic",
                "th": "Thai",
                "hi": "Hindi"
            }
            src_lang = lang_mapping.get(detected, "English")
        except Exception:
            # Fallback thông minh: dự đoán dựa trên từ
            common_english_words = ["hello", "hi", "how", "what", "where", "when", "why", "the", "and", "or"]
            common_vietnamese_words = ["xin", "chào", "là", "của", "và", "có", "tôi", "bạn", "này", "đó"]
            
            text_lower = text.lower()
            if any(word in text_lower for word in common_english_words):
                src_lang = "English"
            elif any(word in text_lower for word in common_vietnamese_words):
                src_lang = "Vietnamese"
            else:
                src_lang = "English"  # Default fallback
    context_note = (
        f"Use terminology appropriate for the field: {domain}."
        if domain else
        "Use general, everyday language."
    )
    # Xác định có phải từ ngắn không (1-2 từ cần giải thích, 3+ từ dịch thẳng)
    words = text.strip().split()
    is_short_phrase = 1 <= len(words) <= 2 and all(w.isalpha() for w in words)
    is_long_phrase = len(words) >= 3  # 3 từ trở lên → dịch thẳng
    if domain and domain.lower() == "slang":
        prompt = (
            f"You are an expert in modern slang and idiomatic expressions.\n"
            f"Translate or interpret the slang phrase below from {src_lang} to {dst_lang}.\n"
            f"Give the most natural and concise equivalent in {dst_lang}.\n"
            f"DO NOT explain or add commentary, just output the translation result.\n\n"
            f"Text: {text}"
)
    elif domain and domain.lower() == "idiom":
        prompt = (
            f"Translate this idiom from {src_lang} to {dst_lang}.\n"
            f"Give ONLY the equivalent expression or meaning.\n"
            f"Do NOT include language labels like 'English:', 'Vietnamese:', etc.\n"
            f"Do NOT add explanations or commentary.\n"
            f"Just output the direct meaning or equivalent idiom.\n\n"
            f"Idiom: {text}"
        )
    elif is_long_phrase:
        # 3+ từ → Dịch thẳng, không giải thích chi tiết
        target_lang_mapping = {
            "vi": "Vietnamese",
            "en": "English", 
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "fr": "French",
            "de": "German",
            "es": "Spanish"
        }
        target_lang_full = target_lang_mapping.get(dst_lang, "Vietnamese")
        
        if domain and domain.lower() == "idiom":
            prompt = (
                f"Translate this idiomatic phrase from {src_lang} to {target_lang_full}.\n"
                f"Give ONLY the equivalent expression or meaning.\n"
                f"Do NOT include language labels or explanations.\n"
                f"Just output the direct meaning.\n\n"
                f"Phrase: {text}"
            )
        elif not domain or domain.lower() in ["daily", "none", ""]:
            prompt = (
                f"You are a direct translator, not an interpreter.\n"
                f"Translate the following text from {src_lang} to {target_lang_full} literally and directly.\n"
                f"Do NOT interpret idioms, slang, or figurative meanings.\n"
                f"Do NOT infer hidden intentions or cultural meanings.\n"
                f"Focus strictly on the literal meaning of each word and phrase.\n"
                f"Keep the translation clear and grammatically natural, but faithful to the original words.\n\n"
                f"Text: {text}"
            )
        else:
            prompt = (
                f"Translate this phrase from {src_lang} to {target_lang_full} in {domain} context:\n"
                f"Use appropriate {domain} terminology.\n"
                f"Just give the translation, no explanations.\n\n"
                f"Phrase: {text}"
            )
    elif is_short_phrase:
        # Xác định ngôn ngữ đích để format chính xác
        target_lang_mapping = {
            "vi": "Vietnamese",
            "en": "English", 
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "fr": "French",
            "de": "German",
            "es": "Spanish"
        }
        target_lang_full = target_lang_mapping.get(dst_lang, "Vietnamese")
        
        # Từ 1-2 từ luôn phải có giải thích chi tiết
        if not domain or domain.lower() in ["none", ""] or domain.lower() == "daily":
            # KHÔNG có ngữ cảnh → Vẫn giải thích cơ bản
prompt = (
                f"You are a professional bilingual dictionary assistant.\n"
                f"Analyze the word '{text}' from {src_lang}.\n"
                f"Provide detailed information in {target_lang_full}.\n\n"
                f"IMPORTANT: All explanations, examples, and the part of speech must be written in {target_lang_full}.\n"
                f"Return your answer in this EXACT format:\n\n"
                f"Nghĩa : <common meaning in {target_lang_full}>\n"
                f"Loại từ : <part of speech in {target_lang_full}>\n"
                f"Phiên âm : <pronunciation - IPA for English target, local pronunciation for others>\n"
                f"Giải thích : <one simple sentence explanation in {target_lang_full}>\n"
                f"1. <example in {domain} context> – <translation in {dst_lang}>\n"
                f"2. <example in {domain} context> – <translation in {dst_lang}>\n"
                f"3. <example in {domain} context> – <translation in {dst_lang}>\n\n"
                f"Word: {text}"
            )
        elif domain and domain.lower() == "idiom":
            # IDIOM cho từ đơn → Rút gọn, không dài dòng
            prompt = (
                f"You are an idiom dictionary.\n"
                f"Explain the word '{text}' if it's part of idioms in {src_lang}.\n"
                f"Provide brief information in {target_lang_full}:\n\n"
                f"Nghĩa : <meaning as idiom or common usage>\n"
                f"Dùng trong : <common idioms or expressions>\n"
                f"Ví dụ : <1-2 short examples>\n\n"
                f"Word: {text}"
            )
        else:
            # CÓ ngữ cảnh khác → Format chi tiết theo domain
            prompt = (
                f"You are a professional bilingual dictionary assistant.\n"
                f"Analyze the word '{text}' from {src_lang} in the context of {domain}.\n"
                f"Provide detailed information in {target_lang_full}.\n\n"
                f"IMPORTANT: All explanations, examples, and the part of speech must be written in {target_lang_full}.\n"
                f"Return your answer in this EXACT format:\n\n"
                f"Nghĩa : <meaning in {domain} context in {target_lang_full}>\n"
                f"Loại từ : <part of speech in {target_lang_full}>\n"
                f"Phiên âm : <pronunciation - IPA for English target, local pronunciation for others>\n"
                f"Giải thích : <one simple sentence explanation for {domain} field in {target_lang_full}>\n"
                f"Ví dụ :\n"
                f"1. <example in {domain} context> – <translation in {dst_lang}>\n"
                f"2. <example in {domain} context> – <translation in {dst_lang}>\n"
                f"3. <example in {domain} context> – <translation in {dst_lang}>\n\n"
                f"Word to analyze: {text}"
            )
    else:
        # Xác định ngôn ngữ đích đầy đủ cho câu dài
target_lang_mapping = {
            "vi": "Vietnamese",
            "en": "English", 
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "fr": "French",
            "de": "German",
            "es": "Spanish"
        }
        target_lang_full = target_lang_mapping.get(dst_lang, "Vietnamese")
        
        #  Prompt cho câu hoặc đoạn với ngôn ngữ rõ ràng
        if not domain or domain.lower() in ["daily", "none", ""] or domain.lower() == "daily":
            # KHÔNG có ngữ cảnh HOẶC Daily → Dịch tự nhiên hàng ngày
            prompt = (
                f"You are a general translator.\n"
                f"Translate the following text from {src_lang} to {target_lang_full}.\n"
                f"Provide natural, everyday translation suitable for daily conversation.\n"
                f"Use common language that everyone can understand.\n"
                f"Make it sound natural and fluent.\n"
                f"Do NOT add explanations or commentary.\n\n"
                f"Text to translate:\n{text}"
            )
        elif domain and domain.lower() == "idiom":
            # IDIOM cho câu dài → Ngắn gọn, tập trung vào ý nghĩa
            prompt = (
                f"You are an idiom interpreter.\n"
                f"Interpret the idiomatic expression from {src_lang} to {target_lang_full}.\n"
                f"Find the equivalent idiom in {target_lang_full}, or explain the meaning briefly.\n"
                f"Keep it concise and natural.\n"
                f"Do NOT provide long explanations.\n\n"
                f"Idiomatic text: {text}"
            )
        else:
            # CÓ ngữ cảnh khác → Dịch theo domain với ý nghĩa tự nhiên
            prompt = (
                f"You are a professional translator specializing in {domain} field.\n"
                f"Translate the following text from {src_lang} to {target_lang_full}.\n"
                f"Use appropriate {domain} terminology and maintain professional tone.\n"
                f"Interpret idioms, slang, and figurative meanings according to {domain} context.\n"
                f"Provide natural translation that sounds native in {target_lang_full}.\n"
                f"Do NOT add explanations, just return the translation.\n\n"
                f"Text to translate:\n{text}"
            )

    # Payload gửi đến Gemini API
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(
            f"{API_URL}?key={API_KEY}",
            json=payload,
            timeout=30
        )
        response.raise_for_status()  # báo lỗi nếu API trả về mã lỗi
        data = response.json()
        # Trích xuất nội dung phản hồi
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"[Error when translating: {e}]"

import requests
from langdetect import detect
from languages import LANGUAGES

#  Thay API_KEY này bằng khóa thật của bạn (từ Google AI Studio)
API_KEY = "AIzaSyDrF1Nq2RUxRJ10CPAYEt1_8bxqq45Of70"

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
    # Xác định có phải 1 từ đơn không (chỉ gồm chữ cái và không có khoảng trắng)
    words = text.strip().split()
    is_short_phrase = 1 <= len(words) <= 2 and all(w.isalpha() for w in words)
    if domain and domain.lower() == "slang":
        prompt = (
            f"You are an expert in modern slang and idiomatic expressions.\n"
            f"Translate or interpret the slang phrase below from {src_lang} to {dst_lang}.\n"
            f"Give the most natural and concise equivalent in {dst_lang}.\n"
            f"DO NOT explain or add commentary, just output the translation result.\n\n"
            f"Text: {text}"
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
        
        #  Prompt cho từ đơn với format chính xác
        prompt = (
            f"You are a professional bilingual dictionary assistant.\n"
            f"Analyze the word '{text}' from {src_lang} and provide detailed information in {target_lang_full}.\n"
            f"Context: {domain}\n\n"
            f"IMPORTANT: Provide ALL explanations, part of speech, and examples in {target_lang_full} only.\n"
            f"Return your answer in this EXACT format:\n\n"
            f"Nghĩa : <meaning in {target_lang_full}>\n"
            f"Loại từ : <part of speech in {target_lang_full}>\n"
            f"Phiên âm : <pronunciation - IPA for English target, local pronunciation for others>\n"
            f"Giải thích : <detailed explanation in {target_lang_full}>\n"
            f"Ví dụ :\n"
            f"1. <example sentence in {src_lang}> – <translation in {dst_lang}>\n"
            f"2. <example sentence in {src_lang}> – <translation in {dst_lang}>\n"
            f"3. <example sentence in {src_lang}> – <translation in {dst_lang}>\n\n"
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
        if not domain or domain.lower() in ["daily", "none", ""]:
             prompt = (
                f"You are a professional translator.\n"
                f"Translate the following text from {src_lang} to {target_lang_full}.\n"
                f"Provide natural, accurate translation while preserving the original meaning.\n"
                f"Do NOT add explanations or commentary, just return the translation.\n\n"
                f"Text to translate:\n{text}"
            )
        else:
            prompt = (
                f"You are a professional translator specializing in {domain} field.\n"
                f"Translate the following text from {src_lang} to {target_lang_full}.\n"
                f"Use appropriate {domain} terminology and maintain professional tone.\n"
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


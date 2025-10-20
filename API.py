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
            src_lang = detected
        except Exception:
            src_lang = "auto"
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
        #  Prompt cho từ đơn — ngắn gọn, đúng định dạng
        prompt = (
            f"You are a bilingual dictionary assistant.\n"
            f"The user is reading a text in the field of '{domain}', and wants to understand the word below in that specific context.\n"
            f"Source language: {src_lang}, Target language: {dst_lang}.\n"
            f"Explain the word ONLY in the given context.\n"
            f"IPA Pronunciation:\n"
            f"- If target language is English → provide IPA of the English translation.\n"
            f"- If target language is NOT English → provide IPA of {dst_lang}.\n\n"
            f"- IPA of the translated word in {dst_lang}. If IPA is not supported or not standard in that language, return an empty string or write 'N/A'\n"
            f"Return your answer ONLY in the following exact format (no extra text):\n\n"
            f"Nghĩa : <nghĩa ngắn gọn bằng {dst_lang}>\n"
            f"Loại từ : <tên loại từ bằng {src_lang}> (<tên loại từ {dst_lang}>)\n"
            f"Phiên âm : <Phiên âm IPA theo hướng dẫn trên>\n"
            f"Giải thích : <giải thích ngắn nghĩa theo lĩnh vực {domain} bằng {src_lang} > – <dịch sang {dst_lang}>\n"
            f"Ví dụ :\n"
            f"1. <câu ví dụ 1 > – <dịch nghĩa sang {dst_lang}>\n"
            f"2. <câu ví dụ 2 > – <dịch nghĩa {dst_lang}\n"
            f"3. <câu ví dụ 3 > – <dịch nghĩa {dst_lang}>\n\n"
            f"Word: {text}"
        )
    else:
        #  Prompt cho câu hoặc đoạn
        if not domain or domain.lower() in ["daily", "none", ""]:
             prompt = (
                f"You are a neutral translator.\n"
                f"Translate the following text from {src_lang} to {dst_lang} literally.\n"
                f"Do NOT interpret idioms, slang, or figurative meanings.\n"
                f"Preserve structure, punctuation, and literal meaning exactly.\n\n"
                f"Text:\n{text}"
            )
        else:
            prompt = (
                f"You are a professional translator. Translate the following text "
                f"from {src_lang} to {dst_lang}. "
                f"Preserve formatting, punctuation, and meaning.\n"
                f"If the text contains idioms, translate them into their natural and equivalent idiomatic expression in {dst_lang}, "
                f"without providing explanations or literal meanings.\n\n"
                f"Text:\n{text}"
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


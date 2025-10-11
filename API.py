import requests

API_KEY = "AIzaSyDrF1Nq2RUxRJ10CPAYEt1_8bxqq45Of70" 
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

LANGUAGES = {
    "Auto Detect": "auto",
    "Tiếng Việt": "vi",
    "Tiếng Anh": "en",
    "Tiếng Nhật": "ja",
    "Tiếng Pháp": "fr",
    "Tiếng Trung": "zh",
    "Tiếng Hàn": "ko",
    "Tiếng Đức": "de",
    "Tiếng Thái": "th",
    "Tiếng Indonesia": "id",
}

CONTEXTS = [
    "General", "Medical/Healthcare", "Technical/IT", "Legal/Contracts",
    "Business/Work", "Gaming/Entertainment", "Travel/Tourism", "Study/Education"
]


def translate_text(text, src_lang="auto", dst_lang="en", domain="General"):
    """Dịch văn bản bằng Gemini API"""
    if not text.strip():
        return ""

    # Prompt hướng dẫn cho AI
    prompt = (
        f"You are a professional translator. Translate this text "
        f"from {src_lang} to {dst_lang}. "
        f"Preserve formatting and punctuation. "
        f"Domain: {domain}.\n\n"
        f"Text:\n{text}"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        response = requests.post(
            f"{API_URL}?key={API_KEY}",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"[Error when translating: {e}]"

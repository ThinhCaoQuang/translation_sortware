from gtts import gTTS
import pygame
import tempfile
import os

# Bản đồ mã ngôn ngữ thân thiện -> mã ngôn ngữ của gTTS
GTTS_LANG_MAP = {
    "vi": "vi",        # Tiếng Việt
    "en": "en",        # Tiếng Anh
    "ja": "ja",        # Tiếng Nhật
    "fr": "fr",        # Tiếng Pháp
    "zh": "zh-CN",     # Tiếng Trung giản thể
    "ko": "ko",        # Tiếng Hàn
    "de": "de",        # Tiếng Đức
    "id": "id",        # Tiếng Indonesia
    "th": "th",        # Tiếng Thái
    # Thêm nếu cần
}

def speak(text: str, lang_code: str = "en"):
    """Đọc nội dung text bằng giọng nói phù hợp với mã ngôn ngữ"""
    if not text.strip():
        return

    lang = GTTS_LANG_MAP.get(lang_code, "en")  # fallback là English

    try:
        # Tạo file âm thanh tạm thời
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            temp_path = fp.name
            tts.save(temp_path)

        # Phát âm thanh bằng pygame
        pygame.mixer.init()
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue

        # Dọn dẹp
        pygame.mixer.music.unload()
        os.remove(temp_path)

    except Exception as ex:
        raise RuntimeError(f"TTS lỗi: {ex}")

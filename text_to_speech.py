from gtts import gTTS
import pygame
import tempfile
import os
from languages import LANGUAGES


# Bản đồ mã ngôn ngữ thân thiện -> mã ngôn ngữ của gTTS
GTTS_LANG_MAP = {
    "vi": "vi",        # Tiếng Việt
    "en": "en",        # Tiếng Anh
    "ja": "ja",        # Tiếng Nhật
    "fr": "fr",        # Tiếng Pháp
    "zh-tw": "zh-tw",  # Tiếng Trung phồn thể
    "zh": "zh",     # Tiếng Trung giản thể
    "ko": "ko",        # Tiếng Hàn
    "de": "de",        # Tiếng Đức
    "id": "id",        # Tiếng Indonesia
    "th": "th",        # Tiếng Thái
    # Thêm nếu cần
}

def speak(text: str, lang_display: str = "Tiếng Anh"):
    if not text.strip():
        return

    # B1: lấy mã từ tên hiển thị ("Tiếng Việt" -> "vi")
    lang_code = LANGUAGES.get(lang_display, lang_display)

    # B2: lấy mã của gTTS (vì một số khác biệt, ví dụ "zh" → "zh-CN")
    lang = GTTS_LANG_MAP.get(lang_code, lang_code)

    try:
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            temp_path = fp.name
            tts.save(temp_path)

        pygame.mixer.init()
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()
        
        # Chờ cho đến khi phát xong hoặc bị dừng
        import time
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)  # Check mỗi 100ms
            continue

        pygame.mixer.music.unload()
        os.remove(temp_path)

    except Exception as ex:
        raise RuntimeError(f"TTS lỗi: {ex}")

def stop_speaking():
    """Dừng phát âm thanh TTS"""
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        return True
    except:
        return False

def is_speaking():
    """Kiểm tra xem có đang phát âm thanh không"""
    try:
        if pygame.mixer.get_init():
            return pygame.mixer.music.get_busy()
        return False
    except:
        return False

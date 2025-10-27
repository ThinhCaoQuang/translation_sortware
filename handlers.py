import flet as ft
import time
import threading
from docx import Document
from api import translate_text, LANGUAGES, CONTEXTS
from text_to_speech import speak, stop_speaking, is_speaking
from speech_to_text import transcribe_audio, start_recording
from languages import LANGUAGES
from history import init_db, add_history, get_history

# Pre-import OCR dependencies để tránh delay lần đầu
try:
    from PIL import Image
    import pytesseract
    import os
    PIL_AVAILABLE = True
    
    # Cache Tesseract path ngay từ đầu
    TESSERACT_CMD = None
    tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\tesseract\tesseract.exe",
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            TESSERACT_CMD = path
            pytesseract.pytesseract.tesseract_cmd = path
            break
except ImportError:
    PIL_AVAILABLE = False


def _lang_code(display: str) -> str:
    """Chuyển đổi tên hiển thị thành mã ngôn ngữ"""
    return LANGUAGES.get(display, "auto")
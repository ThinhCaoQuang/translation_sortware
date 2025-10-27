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
    
Tạo lớp khởi tạo phần mềm
class AppState:
    """Class để lưu trữ trạng thái của ứng dụng"""
    def __init__(self):
        self.realtime_enabled = True  # Bật mặc định
        self.typing_timer = None
        self.translation_cache = {}
        self.recording = False
        self.speaking = False
        self.realtime_translating = False
        self.recording_thread = None
        self.last_audio_data = None  # Lưu audio data để xử lý sau khi dừng
        self.force_stop_recording = False  # Flag để dừng recording ngay lập tức
        
class ThemeHandler:
    """Xử lý chế độ theme và màu sắc"""
    
    @staticmethod
    def get_page_bgcolor(page):
        return ft.Colors.GREY_50 if page.theme_mode == "light" else ft.Colors.GREY_900
    
    @staticmethod
    def get_snackbar_colors(page):
        if page.theme_mode == "light":
            return {
                "content_color": ft.Colors.BLACK87,
                "bgcolor": ft.Colors.with_opacity(0.9, ft.Colors.BLUE_GREY_100)
            }
        else:
            return {
                "content_color": ft.Colors.WHITE,
                "bgcolor": ft.Colors.with_opacity(0.9, ft.Colors.BLUE_GREY_800)
            }
    
    @staticmethod
    def get_dropdown_bgcolor(page):
        return ft.Colors.WHITE if page.theme_mode == "light" else ft.Colors.BLUE_GREY_800
    
    @staticmethod
    def get_textfield_bgcolor(page):
        return ft.Colors.WHITE if page.theme_mode == "light" else ft.Colors.BLUE_GREY_900
    
    @staticmethod
    def get_container_bgcolor(page, color_light, color_dark):
        return color_light if page.theme_mode == "light" else color_dark
    
    @staticmethod
    def get_border_color(page, base_color):
        if page.theme_mode == "light":
            return base_color
        else:
            return ft.Colors.with_opacity(0.6, base_color)
    
    @staticmethod
    def get_text_color(page):
        return ft.Colors.BLACK87 if page.theme_mode == "light" else ft.Colors.WHITE70
    
    @staticmethod
    def get_history_text_color(page):
        return ft.Colors.BLACK87 if page.theme_mode == "light" else ft.Colors.WHITE70

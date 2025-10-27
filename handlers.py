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
        Bổ sung handler chức năng dịch + file văn bản và hình ảnh
class TranslationHandler:
    """Xử lý các chức năng dịch thuật"""
    
    def __init__(self, app_state: AppState):
        self.app_state = app_state
    
    def do_translate(self, e, page, input_text, output_text, src_lang, dst_lang,
                    domain_dd, use_context, translate_btn, loading_ring, prog,
                    history_container, last_history):
        """Xử lý dịch thủ công"""
        text = (input_text.value or "").strip()
        if not text:
            page.snack_bar.content.value = "⚠ Vui lòng nhập nội dung"
            page.snack_bar.open = True
            page.update()
            return

        src_code = _lang_code(src_lang.value)
        dst_code = _lang_code(dst_lang.value)
        domain = domain_dd.value if use_context.value else None

        # Khi bắt đầu dịch
        translate_btn.text = "⏳ Đang dịch..."
        translate_btn.disabled = True
        loading_ring.visible = True
        prog.visible = True
        page.update()

        def worker():
            try:
                # Progress steps cho manual translate
                prog.value = 0.2
                page.update()
                
                result = translate_text(text, src_code, dst_code, domain)
                
                prog.value = 0.9
                page.update()
            except Exception as ex:
                result = f"[Lỗi] {ex}"
            
            try:
                add_history(src_code, dst_code, text, result, domain)
            except:
                pass  # Tránh lỗi khi lưu lịch sử
            
            # Cập nhật lịch sử nếu đang hiển thị
            if history_container.visible:
                self._update_history_display(last_history, page)
            
            # Khi hoàn tất → trả lại trạng thái nút ban đầu
            output_text.value = result
            translate_btn.text = "Dịch"
            translate_btn.disabled = False
            loading_ring.visible = False
            prog.visible = False
            page.update()

        page.run_thread(worker)
    
    def _update_history_display(self, last_history, page):
        """Cập nhật hiển thị lịch sử"""
        items = get_history()
        if items:
            recent_items = items[:5] if len(items) >= 5 else items
            history_text = ""
            
            for i, (src, dst, text_in, text_out, ctx, created) in enumerate(recent_items, 1):
                history_text += f"📅 {created} | {src} → {dst}\n"
                history_text += f"📝 Đầu vào: {text_in[:50]}{'...' if len(text_in) > 50 else ''}\n"
                history_text += f"✅ Kết quả: {text_out[:50]}{'...' if len(text_out) > 50 else ''}\n"
                if ctx:
                    history_text += f"🏷 Ngữ cảnh: {ctx}\n"
                history_text += "─" * 50 + "\n\n"
last_history.value = history_text.strip()
            last_history.color = ThemeHandler.get_history_text_color(page)


class FileHandler:
    """Xử lý các chức năng file"""
    
    @staticmethod
    def on_pick_txt(e: ft.FilePickerResultEvent, input_text, page):
        """Xử lý khi chọn file text"""
        if e.files:
            p = e.files[0].path
            try:
                if p.endswith(".docx"):
                    doc = Document(p)
                    input_text.value = "\n".join([para.text for para in doc.paragraphs])
                else:
                    with open(p, "r", encoding="utf-8", errors="ignore") as rf:
                        input_text.value = rf.read()
            except Exception as ex:
                input_text.value = f"[Lỗi đọc file: {ex}]"
        page.update()
    
    @staticmethod
    def on_pick_image(e: ft.FilePickerResultEvent, input_text, img_btn, page,
                     src_lang, do_translate_callback):
        """Xử lý khi chọn file ảnh để OCR"""
        if not e.files:
            return
            
        img_path = e.files[0].path
        
        # Hiển thị loading và update ngay
        img_btn.icon = ft.Icons.HOURGLASS_EMPTY
        img_btn.tooltip = "🔄 Đang xử lý..."
        page.update()
        
        def process_ocr():
            try:
                if not PIL_AVAILABLE:
                    raise ImportError("PIL không có sẵn")
                
                if not TESSERACT_CMD:
                    raise FileNotFoundError("Không tìm thấy Tesseract OCR")
                
                # Mở ảnh với optimization
                img = Image.open(img_path)
                
                # Tối ưu kích thước ảnh cho tốc độ
                width, height = img.size
                
                # Chỉ resize nếu ảnh quá nhỏ hoặc quá lớn
                if width < 600 or height < 600:
                    scale = min(800/width, 800/height, 2.0)
                    new_size = (int(width * scale), int(height * scale))
                    img = img.resize(new_size, Image.Resampling.BILINEAR)
                elif width > 2000 or height > 2000:
                    scale = min(1500/width, 1500/height)
                    new_size = (int(width * scale), int(height * scale))
                    img = img.resize(new_size, Image.Resampling.BILINEAR)
                
                # Tối ưu ngôn ngữ OCR
                src_code = _lang_code(src_lang.value)
                if src_code == "vi":
                    ocr_lang = "vie"
                elif src_code == "en":
                    ocr_lang = "eng"
                elif src_code == "ja":
                    ocr_lang = "jpn"
                elif src_code == "zh" or src_code == "zh-tw":
                    ocr_lang = "chi_sim"
                elif src_code == "ko":
                    ocr_lang = "kor"
                else:
ocr_lang = "vie+eng"
                
                # Config OCR tối ưu cho tốc độ
                config = "--oem 3 --psm 6"
                
                # Thực hiện OCR
                text = pytesseract.image_to_string(img, lang=ocr_lang, config=config)
                
                # Làm sạch text
                text = text.strip()
                if text:
                    text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
                    input_text.value = text
                else:
                    input_text.value = ""
                    
            except Exception as ex:
                input_text.value = ""
            finally:
                # Reset button state
                img_btn.icon = ft.Icons.IMAGE
                img_btn.tooltip = "🖼️ Trích xuất văn bản từ ảnh"
                page.update()
        
        # Chạy OCR trong thread riêng
        threading.Thread(target=process_ocr, daemon=True).start()



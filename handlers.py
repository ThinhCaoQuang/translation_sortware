"""
File chứa các hàm xử lý chức năng cho ứng dụng dịch thuật
Bao gồm: translate, file operations, audio, theme handling, etc.
"""

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


class AppState:
    """Class để lưu trữ trạng thái của ứng dụng"""
    def __init__(self):
        self.realtime_enabled = False
        self.typing_timer = None
        self.translation_cache = {}
        self.recording = False
        self.speaking = False
        self.realtime_translating = False
        self.recording_thread = None


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


class TranslationHandler:
    """Xử lý các chức năng dịch thuật"""
    
    def __init__(self, app_state: AppState):
        self.app_state = app_state
    
    def toggle_realtime(self, e, page, translate_btn, loading_ring, prog, 
                       realtime_indicator):
        """Bật/tắt chế độ dịch tự động"""
        self.app_state.realtime_enabled = e.control.value
        
        # Ẩn/hiện nút dịch thủ công và các thành phần liên quan
        translate_btn.visible = not self.app_state.realtime_enabled
        loading_ring.visible = False if self.app_state.realtime_enabled else loading_ring.visible
        prog.visible = False if self.app_state.realtime_enabled else prog.visible
        realtime_indicator.visible = self.app_state.realtime_enabled
        
        if self.app_state.realtime_enabled:
            page.snack_bar.content.value = "⚡ Đã bật dịch tự động - Gõ để dịch ngay lập tức"
            # Reset trạng thái nút dịch khi ẩn
            translate_btn.text = "Dịch"
            translate_btn.disabled = False
        else:
            page.snack_bar.content.value = "⏸ Đã tắt dịch tự động - Sử dụng nút dịch thủ công"
        
        page.snack_bar.open = True
        page.update()
    
    def on_input_change(self, e, page, input_text, output_text, prog, 
                       src_lang, dst_lang, domain_dd, use_context,
                       history_container, last_history):
        """Xử lý khi text input thay đổi"""
        if not input_text.value.strip():
            output_text.value = ""
            prog.visible = False
            page.update()
            return
        
        # Nếu realtime được bật
        if self.app_state.realtime_enabled and not self.app_state.realtime_translating:
            # Hủy timer cũ nếu có
            if self.app_state.typing_timer:
                self.app_state.typing_timer.cancel()
            
            # Tạo timer mới - dịch sau 1.0 giây ngừng gõ
            def delayed_translate():
                self.app_state.typing_timer = None
                
                text = input_text.value.strip()
                if not text or len(text) < 2:
                    return
                
                # Tránh dịch lại nếu đang dịch hoặc text không đổi
                if self.app_state.realtime_translating:
                    return
                
                # Bắt đầu dịch - hiển thị progress
                self.app_state.realtime_translating = True
                prog.visible = True
                prog.value = None  # Indeterminate progress
                page.update()
                
                src_code = _lang_code(src_lang.value)
                dst_code = _lang_code(dst_lang.value)
                domain = domain_dd.value if use_context.value else None
                
                def realtime_worker():
                    try:
                        # Tạo cache key
                        cache_key = f"{text}_{src_code}_{dst_code}_{domain}"
                        
                        # Kiểm tra cache trước
                        if cache_key in self.app_state.translation_cache:
                            prog.value = 0.9
                            page.update()
                            result = self.app_state.translation_cache[cache_key]
                        else:
                            # Translate mới
                            prog.value = 0.3
                            page.update()
                            
                            result = translate_text(text, src_code, dst_code, domain)
                            
                            # Lưu vào cache (giới hạn 100 items để tránh memory leak)
                            if len(self.app_state.translation_cache) > 100:
                                # Xóa item cũ nhất
                                first_key = next(iter(self.app_state.translation_cache))
                                del self.app_state.translation_cache[first_key]
                            self.app_state.translation_cache[cache_key] = result
                        
                        prog.value = 0.8
                        page.update()
                        
                        output_text.value = result
                        
                        # Lưu vào lịch sử nếu dịch thành công và text đủ dài
                        if len(text) > 5:
                            add_history(src_code, dst_code, text, result, domain)
                        
                        # Cập nhật lịch sử nếu đang hiển thị
                        if history_container.visible:
                            self._update_history_display(last_history, page)
                        
                    except Exception as ex:
                        # Không hiển thị lỗi cho realtime để tránh spam
                        output_text.value = ""
                    finally:
                        # Reset trạng thái và ẩn progress
                        self.app_state.realtime_translating = False
                        prog.visible = False
                        prog.value = 1.0
                        page.update()
                
                page.run_thread(realtime_worker)
            
            # Import timer với thời gian giảm
            self.app_state.typing_timer = threading.Timer(1.0, delayed_translate)
            self.app_state.typing_timer.start()
    
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
                     src_lang, realtime_enabled, do_translate_callback):
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
                    
                    # Tự động dịch nếu realtime bật
                    if realtime_enabled and text:
                        threading.Timer(0.3, lambda: do_translate_callback(None)).start()
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


class AudioHandler:
    """Xử lý các chức năng âm thanh"""
    
    def __init__(self, app_state: AppState):
        self.app_state = app_state
    
    def do_speak(self, e, page, output_text, speak_btn, dst_lang):
        """Xử lý text-to-speech"""
        # Nếu đang phát, thì dừng lại
        if self.app_state.speaking or is_speaking():
            stop_speaking()
            self.app_state.speaking = False
            speak_btn.icon = ft.Icons.VOLUME_UP
            speak_btn.tooltip = "🔊 Đọc kết quả dịch"
            page.snack_bar.content.value = "⏸ Đã dừng đọc"
            page.snack_bar.open = True
            page.update()
            return
        
        # Nếu không có text thì không làm gì
        if not output_text.value or not output_text.value.strip():
            page.snack_bar.content.value = "⚠ Chưa có kết quả dịch để đọc"
            page.snack_bar.open = True
            page.update()
            return
            
        # Bắt đầu phát
        try:
            self.app_state.speaking = True
            speak_btn.icon = ft.Icons.STOP
            speak_btn.tooltip = "⏸️ Dừng đọc"
            page.update()
            
            def speak_thread():
                try:
                    speak(output_text.value, _lang_code(dst_lang.value))
                except Exception as ex:
                    page.snack_bar.content.value = f"🔊 TTS lỗi: {ex}"
                    page.snack_bar.open = True
                finally:
                    self.app_state.speaking = False
                    speak_btn.icon = ft.Icons.VOLUME_UP
                    speak_btn.tooltip = "🔊 Đọc kết quả dịch"
                    page.update()
            
            threading.Thread(target=speak_thread, daemon=True).start()
            
        except Exception as ex:
            self.app_state.speaking = False
            speak_btn.icon = ft.Icons.VOLUME_UP
            speak_btn.tooltip = "🔊 Đọc kết quả dịch"
            page.snack_bar.content.value = f"🔊 TTS lỗi: {ex}"
            page.snack_bar.open = True
            page.update()
    
    def stop_recording(self, record_spinner, mic_btn, page):
        """Dừng ghi âm"""
        self.app_state.recording = False
        if self.app_state.recording_thread:
            self.app_state.recording_thread = None
        record_spinner.visible = False
        mic_btn.icon_color = None
        mic_btn.tooltip = "🎤 Ghi âm để dịch"
        page.update()
    
    def do_record(self, e, page, input_text, mic_btn, record_spinner, src_lang):
        """Xử lý speech-to-text"""
        if not self.app_state.recording:
            # Bắt đầu ghi âm
            self.app_state.recording = True
            record_spinner.visible = True
            mic_btn.icon_color = "red"
            mic_btn.tooltip = "🛑 Nhấn lại để dừng"
            page.snack_bar.content.value = "🎤 Đang ghi âm... Nhấn lại để dừng hoặc im lặng 2 giây"
            page.snack_bar.open = True
            page.update()
            
            def record_worker():
                try:
                    import speech_recognition as sr
                    
                    # Khởi tạo recognizer
                    r = sr.Recognizer()
                    r.pause_threshold = 2.0
                    r.timeout = 1.0
                    r.phrase_time_limit = None
                    
                    with sr.Microphone() as source:
                        # Điều chỉnh nhiễu nền
                        r.adjust_for_ambient_noise(source, duration=0.5)
                        
                        if not self.app_state.recording:
                            return
                            
                        audio = r.listen(source, timeout=30, phrase_time_limit=None)
                    
                    if not self.app_state.recording:
                        return
                    
                    # Xác định ngôn ngữ
                    src_code = _lang_code(src_lang.value)
                    if src_code == "auto":
                        src_code = "en"
                    
                    # Mapping cho Google Speech Recognition
                    lang_map = {
                        "vi": "vi-VN", "en": "en-US", "zh": "zh-CN",
                        "ja": "ja-JP", "ko": "ko-KR", "fr": "fr-FR",
                        "de": "de-DE", "es": "es-ES", "it": "it-IT",
                        "pt": "pt-BR", "ru": "ru-RU", "ar": "ar-SA"
                    }
                    
                    recognition_lang = lang_map.get(src_code, "en-US")
                    
                    # Nhận dạng giọng nói
                    try:
                        text = r.recognize_google(audio, language=recognition_lang)
                        if text.strip():
                            input_text.value = text
                            page.snack_bar.content.value = f"✅ Đã chuyển đổi: {text[:40]}{'...' if len(text) > 40 else ''}"
                        else:
                            page.snack_bar.content.value = "⚠ Không phát hiện được giọng nói rõ ràng"
                    
                    except sr.UnknownValueError:
                        page.snack_bar.content.value = "⚠ Không thể nhận dạng giọng nói. Hãy thử nói rõ hơn."
                    except sr.RequestError as ex:
                        page.snack_bar.content.value = f"❌ Lỗi dịch vụ nhận dạng: {str(ex)[:50]}..."
                    except Exception as ex:
                        page.snack_bar.content.value = f"❌ Lỗi: {str(ex)[:50]}..."
                        
                except sr.WaitTimeoutError:
                    page.snack_bar.content.value = "⏰ Hết thời gian chờ. Vui lòng thử lại."
                except Exception as ex:
                    page.snack_bar.content.value = f"❌ Lỗi ghi âm: {str(ex)[:50]}..."
                
                finally:
                    # Reset trạng thái UI
                    self.stop_recording(record_spinner, mic_btn, page)
                    page.snack_bar.open = True
                    page.update()
            
            # Lưu reference thread và chạy
            self.app_state.recording_thread = page.run_thread(record_worker)
            
        else:
            # Dừng ghi âm thủ công
            page.snack_bar.content.value = "⏹️ Đã dừng ghi âm thủ công"
            page.snack_bar.open = True
            self.stop_recording(record_spinner, mic_btn, page)


class HistoryHandler:
    """Xử lý các chức năng lịch sử"""
    
    @staticmethod
    def show_history(e, page, history_container, last_history):
        """Hiển thị/ẩn lịch sử"""
        # Toggle hiển thị history container
        if history_container.visible:
            history_container.visible = False
        else:
            items = get_history()
            if not items:
                page.snack_bar.content.value = "📜 Chưa có lịch sử dịch"
                page.snack_bar.open = True
                page.update()
                return
            
            # Hiển thị 5 lịch sử gần nhất
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
            history_container.visible = True
        
        page.update()
    
    @staticmethod
    def clear_history_action(e, page, last_history, history_container):
        """Xóa lịch sử"""
        import sqlite3
        conn = sqlite3.connect("history.db")
        conn.execute("DELETE FROM history")
        conn.commit()
        conn.close()
        last_history.value = ""
        history_container.visible = False
        page.snack_bar.content.value = "🗑️ Đã xóa toàn bộ lịch sử"
        page.snack_bar.open = True
        page.update()
    
    @staticmethod
    def export_history_action(e, page):
        """Xuất lịch sử ra file"""
        items = get_history()
        if not items:
            page.snack_bar.content.value = "📜 Không có lịch sử để xuất"
            page.snack_bar.open = True
            page.update()
            return
            
        with open("history_export.txt", "w", encoding="utf-8") as f:
            for src, dst, text_in, text_out, ctx, created in items:
                f.write(f"{created} | {src} → {dst} ({ctx or 'Không có ngữ cảnh'})\n")
                f.write(f"Đầu vào: {text_in}\n")
                f.write(f"Kết quả: {text_out}\n\n")
        page.snack_bar.content.value = "💾 Đã xuất ra file history_export.txt"
        page.snack_bar.open = True
        page.update()


class UtilityHandler:
    """Xử lý các chức năng tiện ích"""
    
    @staticmethod
    def do_copy(e, page, output_text):
        """Copy kết quả vào clipboard"""
        page.set_clipboard(output_text.value or "")
        page.snack_bar.content.value = "📋 Đã copy vào clipboard"
        page.snack_bar.open = True
        page.update()
    
    @staticmethod
    def do_swap(e, page, src_lang, dst_lang):
        """Đổi chiều ngôn ngữ"""
        s, d = src_lang.value, dst_lang.value
        src_lang.value, dst_lang.value = d, s
        page.update()
    
    @staticmethod
    def toggle_context(e, page, domain_dd, use_context):
        """Bật/tắt ngữ cảnh chuyên môn"""
        domain_dd.opacity = 1.0 if use_context.value else 0.0
        page.update()
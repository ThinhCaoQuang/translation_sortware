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
        """Dừng ghi âm và reset UI"""
        self.app_state.recording = False
        self.app_state.force_stop_recording = False
        if self.app_state.recording_thread:
            self.app_state.recording_thread = None
        record_spinner.visible = False
        mic_btn.icon_color = None
        mic_btn.tooltip = "🎤 Ghi âm để dịch"
        page.update()
    
    def do_record(self, e, page, input_text, mic_btn, record_spinner, src_lang):
        """Xử lý speech-to-text với các cải tiến"""
        if not self.app_state.recording:
            # Bắt đầu ghi âm
            self.app_state.recording = True
            record_spinner.visible = True
mic_btn.icon_color = "red"
            mic_btn.tooltip = "🛑 Nhấn lại để dừng"
            page.snack_bar.content.value = "🎤 Chuẩn bị ghi âm... Sẽ tự động bắt đầu khi có giọng nói!"
            page.snack_bar.open = True
            page.update()
            
            def record_worker():
                recorded_text = None  # Biến lưu văn bản đã ghi âm
                try:
                    import speech_recognition as sr
                    
                    # Khởi tạo recognizer với cấu hình để bắt từ đầu tiên
                    r = sr.Recognizer()
                    
                    # Cài đặt để bắt được từ đầu tiên
                    r.pause_threshold = 0.8  # Thời gian im lặng để kết thúc
                    r.phrase_time_limit = None  # Không giới hạn thời gian nói
                    r.dynamic_energy_threshold = False  # Tắt auto-adjust để có control tốt hơn
                    r.energy_threshold = 100  # Ngưỡng thấp để bắt giọng nói nhỏ
                    r.non_speaking_duration = 0.2  # Thời gian im lặng trước khi recording
                    
                    with sr.Microphone() as source:
                        # Điều chỉnh nhanh
                        page.snack_bar.content.value = "🔧 Chuẩn bị micro..."
                        page.snack_bar.open = True
                        page.update()
                        
                        # Lấy mẫu nhiễu nền ngắn gọn
                        r.adjust_for_ambient_noise(source, duration=0.2)
                        
                        # Lưu energy threshold sau khi điều chỉnh
                        baseline_energy = r.energy_threshold
                        # Đặt threshold thấp hơn baseline để sensitive hơn
                        r.energy_threshold = max(50, baseline_energy * 0.3)
                        
                        if not self.app_state.recording:
                            return
                        
                        page.snack_bar.content.value = "🎤 NÓI NGAY BÂY GIỜ! Đang lắng nghe..."
                        page.snack_bar.open = True
                        page.update()
                        
                        # Chiến lược mới: Listen với timeout rất ngắn để bắt đầu ngay
                        try:
                            # Thử bắt audio ngay lập tức
                            audio = r.listen(
                                source, 
                                timeout=1,  # Bắt đầu nghe trong 1 giây
                                phrase_time_limit=20  # Cho phép nói tối đa 20 giây
                            )
                        except sr.WaitTimeoutError:
                            # Nếu timeout, thử lần nữa với threshold thấp hơn
                            r.energy_threshold = max(30, r.energy_threshold * 0.5)
page.snack_bar.content.value = "🎤 Đang chờ giọng nói... Hãy nói to hơn!"
                            page.snack_bar.open = True
                            page.update()
                            
                            audio = r.listen(
                                source,
                                timeout=10,
                                phrase_time_limit=20
                            )
                    
                    # Kiểm tra trạng thái ghi âm trước khi xử lý
                    if not self.app_state.recording:
                        # Nếu bị dừng thủ công, vẫn cố gắng xử lý audio đã ghi
                        pass
                    
                    page.snack_bar.content.value = "🔄 Đang xử lý âm thanh..."
                    page.snack_bar.open = True
                    page.update()
                    
                    # Xác định ngôn ngữ với ưu tiên tiếng Việt
                    src_code = _lang_code(src_lang.value)
                    if src_code == "auto":
                        src_code = "vi"  # Mặc định tiếng Việt cho người Việt Nam
                    
                    # Mapping mở rộng cho Google Speech Recognition
                    lang_map = {
                        "vi": "vi-VN", 
                        "en": "en-US", 
                        "zh": "zh-CN",
                        "zh-tw": "zh-TW",
                        "ja": "ja-JP", 
                        "ko": "ko-KR", 
                        "fr": "fr-FR",
                        "de": "de-DE", 
                        "es": "es-ES", 
                        "it": "it-IT",
                        "pt": "pt-BR", 
                        "ru": "ru-RU", 
                        "ar": "ar-SA",
                        "th": "th-TH",
                        "hi": "hi-IN"
                    }
                    
                    recognition_lang = lang_map.get(src_code, "vi-VN")
                    
                    # Thử nhận dạng với ưu tiên ngôn ngữ được chọn
                    recognition_attempts = []
                    
                    # Ưu tiên 1: Ngôn ngữ được chọn cụ thể
                    if src_code != "auto":
                        recognition_attempts.append(recognition_lang)
                    
                    # Ưu tiên 2: Nếu auto detect, thử tiếng Việt trước (cho người Việt)
                    if src_code == "auto":
                        recognition_attempts.append("vi-VN")
                        recognition_attempts.append("en-US")
                    
                    # Ưu tiên 3: Fallback cho các trường hợp đặc biệt
                    if src_code == "vi" and "en-US" not in recognition_attempts:
                        recognition_attempts.append("en-US")  # Fallback cho tiếng Việt
elif src_code == "en" and "vi-VN" not in recognition_attempts:
                        recognition_attempts.append("vi-VN")  # Fallback cho tiếng Anh
                    
                    # Nhận dạng giọng nói với ưu tiên tiếng Việt
                    best_confidence = 0
                    best_text = None
                    best_lang = None
                    
                    for attempt_lang in recognition_attempts:
                        try:
                            # Sử dụng show_all=True để có nhiều tùy chọn
                            alternatives = r.recognize_google(audio, language=attempt_lang, show_all=True)
                            
                            if alternatives and "alternative" in alternatives:
                                for alt in alternatives["alternative"]:
                                    current_confidence = alt.get("confidence", 0.5)  # Default confidence
                                    current_text = alt["transcript"]
                                    
                                    # Bonus điểm cho ngôn ngữ được chọn cụ thể
                                    if attempt_lang == recognition_lang and src_code != "auto":
                                        # Ưu tiên mạnh cho ngôn ngữ được chọn cụ thể
                                        current_confidence += 0.4
                                    elif attempt_lang == "vi-VN" and src_code == "auto":
                                        # Kiểm tra xem có từ tiếng Việt không khi auto detect
                                        vietnamese_words = ["là", "của", "và", "có", "tôi", "bạn", "này", "đó", "lớp", "học", "việt", "nam", "đi", "đến", "với", "trong"]
                                        text_lower = current_text.lower()
                                        has_vietnamese = any(word in text_lower for word in vietnamese_words)
                                        
                                        if has_vietnamese:
                                            current_confidence += 0.3  # Bonus cho tiếng Việt có từ Việt
                                        else:
                                            current_confidence += 0.1  # Bonus nhỏ cho tiếng Việt
                                    elif attempt_lang == "en-US" and src_code == "auto":
                                        # Kiểm tra xem có từ tiếng Anh không khi auto detect  
                                        english_words = ["the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"]
                                        text_lower = current_text.lower()
                                        has_english = any(word in text_lower for word in english_words)
                                        
                                        if has_english:
current_confidence += 0.2  # Bonus cho tiếng Anh có từ Anh
                                    
                                    # Chọn kết quả tốt nhất
                                    if current_confidence > best_confidence:
                                        best_confidence = current_confidence
                                        best_text = current_text
                                        best_lang = attempt_lang
                            else:
                                # Fallback: thử phương thức cũ
                                text = r.recognize_google(audio, language=attempt_lang)
                                if text.strip():
                                    confidence = 0.7 if attempt_lang == "vi-VN" else 0.5
                                    if confidence > best_confidence:
                                        best_confidence = confidence
                                        best_text = text
                                        best_lang = attempt_lang
                                    
                        except sr.UnknownValueError:
                            continue  # Thử ngôn ngữ tiếp theo
                        except sr.RequestError:
                            continue  # Thử ngôn ngữ tiếp theo
                        except Exception:
                            continue  # Thử ngôn ngữ tiếp theo
                    
                    # Sử dụng kết quả tốt nhất
                    if best_text and best_confidence > 0.4:  # Ngưỡng thấp hơn
                        recorded_text = best_text
                    
                    # Xử lý kết quả
                    if recorded_text and recorded_text.strip():
                        # Làm sạch văn bản
                        recorded_text = recorded_text.strip()
                        
                        # Sửa các từ thường bị nhầm lẫn khi nói tiếng Việt
                        if best_lang == "vi-VN" or src_code == "vi":
                            # Dictionary sửa lỗi phổ biến
                            vietnamese_corrections = {
                                "love": "lớp",
                                "Love": "Lớp", 
                                "class": "lớp",
                                "Class": "Lớp",
                                "home": "hôm",
                                "Home": "Hôm",
                                "time": "thời",
                                "Time": "Thời",
                                "name": "năm",
                                "Name": "Năm",
                                "house": "học",
                                "House": "Học",
                                "school": "trường",
                                "School": "Trường",
                                "book": "bước",
                                "Book": "Bước",
"water": "việt",
                                "Water": "Việt",
                                "come": "gọi",
                                "Come": "Gọi",
                                "go": "đi",
                                "Go": "Đi"
                            }
                            
                            # Thay thế từng từ
                            words = recorded_text.split()
                            corrected_words = []
                            for word in words:
                                # Loại bỏ dấu câu để check
                                clean_word = word.strip(".,!?;:")
                                punctuation = word[len(clean_word):]
                                
                                if clean_word in vietnamese_corrections:
                                    corrected_words.append(vietnamese_corrections[clean_word] + punctuation)
                                else:
                                    corrected_words.append(word)
                            
                            recorded_text = " ".join(corrected_words)
                        
                        # Cập nhật UI
                        input_text.value = recorded_text
                        confidence_text = f" (tin cậy: {best_confidence:.1%})" if best_confidence > 0 else ""
                        page.snack_bar.content.value = f"✅ {best_lang}: {recorded_text[:35]}{'...' if len(recorded_text) > 35 else ''}{confidence_text}"
                    else:
                        page.snack_bar.content.value = "⚠ Không thể nhận dạng giọng nói. Thử nói rõ hơn và gần micro."
                        
                except sr.WaitTimeoutError:
                    page.snack_bar.content.value = "⏰ Không nghe thấy giọng nói. Thử nói to hơn hoặc gần micro hơn!"
                except Exception as ex:
                    page.snack_bar.content.value = f"❌ Lỗi ghi âm: {str(ex)[:50]}..."
                
                finally:
                    # Reset trạng thái UI - LUÔN thực hiện
                    self.stop_recording(record_spinner, mic_btn, page)
                    page.snack_bar.open = True
                    page.update()
            
            # Lưu reference thread và chạy
            self.app_state.recording_thread = page.run_thread(record_worker)
            
        else:
            # Dừng ghi âm thủ công - văn bản vẫn được xử lý
            self.app_state.recording = False
            page.snack_bar.content.value = "⏹️ Đang xử lý âm thanh đã ghi..."
            page.snack_bar.open = True
            page.update()



import flet as ft
from docx import Document
from api import translate_text, LANGUAGES, CONTEXTS
from text_to_speech import speak, stop_speaking, is_speaking
from speech_to_text import transcribe_audio, start_recording
from languages import LANGUAGES
from history import init_db, add_history, get_history
import time
import threading

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
    return LANGUAGES.get(display, "auto")


def main(page: ft.Page):
    page.title = "🌐 Translation Studio"
    page.theme_mode = "dark"
    page.window_maximized = True    
    page.padding = 0
    page.vertical_alignment = "start"
    page.scroll = "adaptive"
    
    def get_page_bgcolor():
        return ft.Colors.GREY_50 if page.theme_mode == "light" else ft.Colors.GREY_900
    
    page.bgcolor = get_page_bgcolor()
    
    def get_snackbar_colors():
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
    
    snackbar_colors = get_snackbar_colors()
    page.snack_bar = ft.SnackBar(
        content=ft.Text("", color=snackbar_colors["content_color"]),
        bgcolor=snackbar_colors["bgcolor"],
        duration=3000,
        margin=ft.margin.all(10),
        behavior=ft.SnackBarBehavior.FLOATING
    )
    init_db()


    # -------------------- Language controls --------------------
    def get_dropdown_bgcolor():
        return ft.Colors.WHITE if page.theme_mode == "light" else ft.Colors.BLUE_GREY_800
    
    def get_textfield_bgcolor():
        return ft.Colors.WHITE if page.theme_mode == "light" else ft.Colors.BLUE_GREY_900
    
    def get_container_bgcolor(color_light, color_dark):
        return color_light if page.theme_mode == "light" else color_dark
    
    def get_border_color(base_color):
        if page.theme_mode == "light":
            return base_color
        else:
            return ft.Colors.with_opacity(0.6, base_color)
    
    def get_text_color():
        return ft.Colors.BLACK87 if page.theme_mode == "light" else ft.Colors.WHITE70

    src_lang = ft.Dropdown(
        label="Ngôn ngữ nguồn",
        options=[ft.dropdown.Option(lang) for lang in LANGUAGES.keys()],
        value="Auto Detect",
        width=330,
        border_color=get_border_color(ft.Colors.BLUE_400),
        focused_border_color=get_border_color(ft.Colors.BLUE_600),
        bgcolor=get_dropdown_bgcolor(),
        content_padding=ft.padding.symmetric(horizontal=15, vertical=12),
        text_style=ft.TextStyle(size=14),
    )

    dst_lang = ft.Dropdown(
        label="Ngôn ngữ đích",
        options=[ft.dropdown.Option(lang) for lang in LANGUAGES.keys()],
        value="Tiếng Việt",
        width=330,
        border_color=get_border_color(ft.Colors.GREEN_400),
        focused_border_color=get_border_color(ft.Colors.GREEN_600),
        bgcolor=get_dropdown_bgcolor(),
        content_padding=ft.padding.symmetric(horizontal=15, vertical=12),
        text_style=ft.TextStyle(size=14),
    )
    
    theme_btn = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE, 
        tooltip="🌓 Chuyển chế độ nền",
        style=ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: ft.Colors.AMBER_600},
            bgcolor={ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, ft.Colors.AMBER)},
            overlay_color={ft.ControlState.PRESSED: ft.Colors.with_opacity(0.2, ft.Colors.AMBER)},
        )
    )
    def toggle_theme(e):
        # Thêm hiệu ứng chuyển đổi mượt mà
        page.theme_mode = "light" if page.theme_mode == "dark" else "dark"
        theme_btn.icon = ft.Icons.DARK_MODE if page.theme_mode == "light" else ft.Icons.LIGHT_MODE
        
        # Cập nhật màu nền trang với animation
        page.bgcolor = get_page_bgcolor()
        
        # Cập nhật snackbar
        snackbar_colors = get_snackbar_colors()
        page.snack_bar.content.color = snackbar_colors["content_color"]
        page.snack_bar.bgcolor = snackbar_colors["bgcolor"]
        
        # Cập nhật màu nền dropdowns và textfields
        dropdown_bg = get_dropdown_bgcolor()
        src_lang.bgcolor = dropdown_bg
        dst_lang.bgcolor = dropdown_bg
        domain_dd.bgcolor = dropdown_bg
        
        # Cập nhật border colors cho dropdowns
        src_lang.border_color = get_border_color(ft.Colors.BLUE_400)
        src_lang.focused_border_color = get_border_color(ft.Colors.BLUE_600)
        dst_lang.border_color = get_border_color(ft.Colors.GREEN_400)
        dst_lang.focused_border_color = get_border_color(ft.Colors.GREEN_600)
        domain_dd.border_color = get_border_color(ft.Colors.TEAL_400)
        domain_dd.focused_border_color = get_border_color(ft.Colors.TEAL_600)
        
        textfield_bg = get_textfield_bgcolor()
        input_text.bgcolor = textfield_bg
        output_text.bgcolor = textfield_bg
        
        # Cập nhật border colors cho textfields
        input_text.border_color = get_border_color(ft.Colors.BLUE_400)
        input_text.focused_border_color = get_border_color(ft.Colors.BLUE_600)
        output_text.border_color = get_border_color(ft.Colors.GREEN_400)
        output_text.focused_border_color = get_border_color(ft.Colors.GREEN_600)
        
        # Cập nhật màu containers
        controls_card.bgcolor = get_container_bgcolor(
            ft.Colors.with_opacity(0.8, ft.Colors.WHITE),
            ft.Colors.with_opacity(0.3, ft.Colors.BLUE_GREY_800)
        )
        
        input_container.bgcolor = get_container_bgcolor(
            ft.Colors.with_opacity(0.6, ft.Colors.BLUE_50),
            ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_900)
        )
        
        action_container.bgcolor = get_container_bgcolor(
            ft.Colors.with_opacity(0.6, ft.Colors.TEAL_50),
            ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_900)
        )
        
        output_container.bgcolor = get_container_bgcolor(
            ft.Colors.with_opacity(0.6, ft.Colors.GREEN_50),
            ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_900)
        )
        
        history_container.bgcolor = get_container_bgcolor(
            ft.Colors.with_opacity(0.4, ft.Colors.GREY_100),
            ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_900)
        )
        
        # Cập nhật text colors cho section headers
        input_header = input_container.content.controls[0]
        output_header = output_container.content.controls[0].controls[0]
        
        input_header.color = get_border_color(ft.Colors.BLUE_600)
        output_header.color = get_border_color(ft.Colors.GREEN_600)
        

        
        # Cập nhật history header và text nếu đang hiển thị
        if history_container.visible:
            history_header = history_container.content.controls[0].controls[0]
            history_header.color = get_text_color()
            
        # Cập nhật màu text của lịch sử
        last_history.color = get_history_text_color()
        
        # Cập nhật màu cho toggle realtime
        is_dark = page.theme_mode == "dark"
        toggle_icon = realtime_toggle_container.content.controls[0]
        toggle_text = realtime_toggle_container.content.controls[1]
        toggle_icon.color = ft.Colors.BLUE_400 if is_dark else ft.Colors.BLUE_600
        toggle_text.color = ft.Colors.WHITE70 if is_dark else ft.Colors.BLACK87
        
        # Batch update để chuyển đổi mượt mà
        page.update()
    theme_btn.on_click = toggle_theme

    swap_btn = ft.IconButton(
        icon=ft.Icons.SWAP_HORIZ, 
        tooltip="🔄 Đổi chiều ngôn ngữ",
        style=ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: ft.Colors.PURPLE_600},
            bgcolor={ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, ft.Colors.PURPLE)},
            overlay_color={ft.ControlState.PRESSED: ft.Colors.with_opacity(0.2, ft.Colors.PURPLE)},
        )
    )
    def do_swap(e):
        s, d = src_lang.value, dst_lang.value
        src_lang.value, dst_lang.value = d, s
        page.update()
    swap_btn.on_click = do_swap

    # -------------------- Text fields --------------------
    input_text = ft.TextField(
        label="Nhập văn bản cần dịch",
        multiline=True,
        min_lines=5,
        max_lines=10,
        expand=True,
        border_color=get_border_color(ft.Colors.BLUE_400),
        focused_border_color=get_border_color(ft.Colors.BLUE_600),
        bgcolor=get_textfield_bgcolor(),
        content_padding=ft.padding.all(15),
        text_style=ft.TextStyle(size=16),
    )
    # Biến cho realtime translation
    realtime_enabled = False
    typing_timer = None
    
    # Cache để tăng tốc dịch
    translation_cache = {}
    
    def toggle_realtime(e):
        nonlocal realtime_enabled
        realtime_enabled = e.control.value  # Lấy trạng thái từ switch
        
        # Ẩn/hiện nút dịch thủ công và các thành phần liên quan
        translate_btn.visible = not realtime_enabled
        loading_ring.visible = False if realtime_enabled else loading_ring.visible
        prog.visible = False if realtime_enabled else prog.visible
        realtime_indicator.visible = realtime_enabled
        
        if realtime_enabled:
            page.snack_bar.content.value = "⚡ Đã bật dịch tự động - Gõ để dịch ngay lập tức"
            # Reset trạng thái nút dịch khi ẩn
            translate_btn.text = "Dịch"
            translate_btn.disabled = False
        else:
            page.snack_bar.content.value = "⏸️ Đã tắt dịch tự động - Sử dụng nút dịch thủ công"
        
        page.snack_bar.open = True
        page.update()
    
    # Toggle switch cho realtime với label
    realtime_switch = ft.Switch(
        value=False,
        on_change=toggle_realtime,
        active_color=ft.Colors.GREEN_600,
        inactive_thumb_color=ft.Colors.GREY_400,
        inactive_track_color=ft.Colors.GREY_300,
    )
    
    realtime_toggle_container = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.BOLT, size=18, color=ft.Colors.BLUE_600),
            ft.Text("Dịch tự động", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK87),
            realtime_switch,
        ], spacing=8, alignment=ft.MainAxisAlignment.END),
        padding=ft.padding.symmetric(horizontal=8, vertical=4),
        border_radius=8,
    )
    
    # Indicator trạng thái realtime
    realtime_indicator = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.AUTORENEW, size=14, color=ft.Colors.WHITE),
            ft.Text("AUTO", size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
        ], spacing=3, alignment=ft.MainAxisAlignment.CENTER),
        visible=False,
        animate_opacity=300,
        padding=ft.padding.symmetric(horizontal=8, vertical=4),
        bgcolor=ft.Colors.GREEN_600,
        border_radius=12,
        width=65,
        height=26,
    )

    def on_input_change(e):
        nonlocal typing_timer, realtime_translating
        
        if not input_text.value.strip():
            output_text.value = ""
            prog.visible = False
            page.update()
            return
        
        # Nếu realtime được bật
        if realtime_enabled and not realtime_translating:
            # Hủy timer cũ nếu có
            if typing_timer:
                typing_timer.cancel()
            
            # Tạo timer mới - dịch sau 1.0 giây ngừng gõ (giảm từ 1.5s)
            def delayed_translate():
                nonlocal typing_timer, realtime_translating
                typing_timer = None
                
                text = input_text.value.strip()
                if not text or len(text) < 2:  # Giảm threshold xuống 2 ký tự
                    return
                
                # Tránh dịch lại nếu đang dịch hoặc text không đổi
                if realtime_translating:
                    return
                
                # Bắt đầu dịch - hiển thị progress
                realtime_translating = True
                prog.visible = True
                prog.value = None  # Indeterminate progress
                page.update()
                
                src_code = _lang_code(src_lang.value)
                dst_code = _lang_code(dst_lang.value)
                domain = domain_dd.value if use_context.value else None
                
                def realtime_worker():
                    nonlocal realtime_translating, translation_cache
                    try:
                        # Tạo cache key
                        cache_key = f"{text}_{src_code}_{dst_code}_{domain}"
                        
                        # Kiểm tra cache trước
                        if cache_key in translation_cache:
                            prog.value = 0.9
                            page.update()
                            result = translation_cache[cache_key]
                        else:
                            # Translate mới
                            prog.value = 0.3
                            page.update()
                            
                            result = translate_text(text, src_code, dst_code, domain)
                            
                            # Lưu vào cache (giới hạn 100 items để tránh memory leak)
                            if len(translation_cache) > 100:
                                # Xóa item cũ nhất
                                first_key = next(iter(translation_cache))
                                del translation_cache[first_key]
                            translation_cache[cache_key] = result
                        
                        prog.value = 0.8
                        page.update()
                        
                        output_text.value = result
                        
                        # Lưu vào lịch sử nếu dịch thành công và text đủ dài
                        if len(text) > 5:  # Chỉ lưu text dài để tránh spam
                            add_history(src_code, dst_code, text, result, domain)
                        
                        # Cập nhật lịch sử nếu đang hiển thị
                        if history_container.visible:
                            items = get_history()
                            if items:
                                recent_items = items[:5] if len(items) >= 5 else items
                                history_text = ""
                                
                                for i, (src, dst, text_in, text_out, ctx, created) in enumerate(recent_items, 1):
                                    history_text += f"🔹 {created} | {src} → {dst}\n"
                                    history_text += f"📝 Đầu vào: {text_in[:50]}{'...' if len(text_in) > 50 else ''}\n"
                                    history_text += f"✨ Kết quả: {text_out[:50]}{'...' if len(text_out) > 50 else ''}\n"
                                    if ctx:
                                        history_text += f"🏷️ Ngữ cảnh: {ctx}\n"
                                    history_text += "─" * 50 + "\n\n"
                                
                                last_history.value = history_text.strip()
                                last_history.color = get_history_text_color()
                        
                    except Exception as ex:
                        # Không hiển thị lỗi cho realtime để tránh spam
                        output_text.value = ""
                    finally:
                        # Reset trạng thái và ẩn progress
                        realtime_translating = False
                        prog.visible = False
                        prog.value = 1.0
                        page.update()
                
                page.run_thread(realtime_worker)
            
            # Import timer với thời gian giảm
            import threading
            typing_timer = threading.Timer(1.0, delayed_translate)  # Giảm từ 1.5s xuống 1.0s
            typing_timer.start()
    
    input_text.on_change = on_input_change

    output_text = ft.TextField(
        label="Kết quả dịch",
        multiline=True,
        min_lines=5,
        max_lines=10,
        expand=True,
        read_only=True,
        border_color=get_border_color(ft.Colors.GREEN_400),
        focused_border_color=get_border_color(ft.Colors.GREEN_600),
        bgcolor=get_textfield_bgcolor(),
        content_padding=ft.padding.all(15),
        text_style=ft.TextStyle(size=16, weight=ft.FontWeight.W_500),
    )
    def get_history_text_color():
        return ft.Colors.BLACK87 if page.theme_mode == "light" else ft.Colors.WHITE70

    last_history = ft.Text(
        "", 
        selectable=True, 
        size=14, 
        color=get_history_text_color(),
        style=ft.TextStyle(weight=ft.FontWeight.W_400)
    )


    # -------------------- Context / Domain --------------------
    use_context = ft.Checkbox(
        label="Dịch theo ngữ cảnh chuyên môn",
        check_color=ft.Colors.TEAL_600,
        active_color=ft.Colors.TEAL_400,
        label_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_500)
    )
    domain_dd = ft.Dropdown(
        label="Lĩnh vực chuyên môn",
        options=[ft.dropdown.Option(x) for x in CONTEXTS],
        value="Daily",
        width=300,
        opacity=0,
        animate_opacity=300,
        border_color=get_border_color(ft.Colors.TEAL_400),
        focused_border_color=get_border_color(ft.Colors.TEAL_600),
        bgcolor=get_dropdown_bgcolor(),
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
        text_style=ft.TextStyle(size=14),
    )
    def toggle_context(e):
        domain_dd.opacity = 1.0 if use_context.value else 0.0
        page.update()
    use_context.on_change = toggle_context

    # -------------------- File pickers --------------------
    pick_txt = ft.FilePicker()
    pick_img = ft.FilePicker()
    page.overlay.append(pick_txt)
    page.overlay.append(pick_img)

    def on_pick_txt(e: ft.FilePickerResultEvent):
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
    pick_txt.on_result = on_pick_txt

    def on_pick_image(e: ft.FilePickerResultEvent):
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
                    # Ảnh nhỏ - tăng kích thước nhẹ
                    scale = min(800/width, 800/height, 2.0)
                    new_size = (int(width * scale), int(height * scale))
                    img = img.resize(new_size, Image.Resampling.BILINEAR)
                elif width > 2000 or height > 2000:
                    # Ảnh quá lớn - giảm kích thước để tăng tốc
                    scale = min(1500/width, 1500/height)
                    new_size = (int(width * scale), int(height * scale))
                    img = img.resize(new_size, Image.Resampling.BILINEAR)
                
                # Tối ưu ngôn ngữ OCR - ít ngôn ngữ hơn = nhanh hơn
                src_code = _lang_code(src_lang.value)
                if src_code == "vi":
                    ocr_lang = "vie"  # Chỉ Việt
                elif src_code == "en":
                    ocr_lang = "eng"  # Chỉ Anh
                elif src_code == "ja":
                    ocr_lang = "jpn"
                elif src_code == "zh" or src_code == "zh-tw":
                    ocr_lang = "chi_sim"
                elif src_code == "ko":
                    ocr_lang = "kor"
                else:
                    ocr_lang = "vie+eng"  # Auto detect - chỉ 2 ngôn ngữ chính
                
                # Config OCR tối ưu cho tốc độ
                config = "--oem 3 --psm 6"
                
                # Thực hiện OCR
                text = pytesseract.image_to_string(img, lang=ocr_lang, config=config)
                
                # Làm sạch text nhanh
                text = text.strip()
                if text:
                    # Làm sạch đơn giản hơn
                    text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
                    input_text.value = text
                    
                    # Tự động dịch nếu realtime bật
                    if realtime_enabled and text:
                        import threading
                        threading.Timer(0.3, lambda: do_translate(None)).start()  # Giảm delay
                else:
                    input_text.value = ""
                    
            except FileNotFoundError as ex:
                input_text.value = ""
            except Exception as ex:
                input_text.value = ""
            finally:
                # Reset button state
                img_btn.icon = ft.Icons.IMAGE
                img_btn.tooltip = "🖼️ Trích xuất văn bản từ ảnh"
                page.update()
        
        # Chạy OCR trong thread riêng
        import threading
        threading.Thread(target=process_ocr, daemon=True).start()

    pick_img.on_result = on_pick_image

    file_btn = ft.IconButton(
        icon=ft.Icons.UPLOAD_FILE,
        tooltip="📄 Mở file .txt/.docx",
        on_click=lambda e: pick_txt.pick_files(allow_multiple=False, allowed_extensions=["txt", "docx"]),
        style=ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: ft.Colors.INDIGO_600},
            bgcolor={ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, ft.Colors.INDIGO)},
            overlay_color={ft.ControlState.PRESSED: ft.Colors.with_opacity(0.2, ft.Colors.INDIGO)},
        )
    )
    img_btn = ft.IconButton(
        icon=ft.Icons.IMAGE,
        tooltip="🖼️ Trích xuất văn bản từ ảnh",
        on_click=lambda e: pick_img.pick_files(
            allow_multiple=False, 
            allowed_extensions=["jpg", "jpeg", "png", "bmp", "tiff", "tif", "webp"]
        ),
        style=ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: ft.Colors.PINK_600},
            bgcolor={ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, ft.Colors.PINK)},
            overlay_color={ft.ControlState.PRESSED: ft.Colors.with_opacity(0.2, ft.Colors.PINK)},
        )
    )

    # -------------------- Copy / Speak --------------------
    copy_btn = ft.IconButton(
        icon=ft.Icons.CONTENT_COPY, 
        tooltip="📋 Copy kết quả",
        style=ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: ft.Colors.CYAN_600},
            bgcolor={ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, ft.Colors.CYAN)},
            overlay_color={ft.ControlState.PRESSED: ft.Colors.with_opacity(0.2, ft.Colors.CYAN)},
        )
    )

    def do_copy(e):
        page.set_clipboard(output_text.value or "")
        page.snack_bar.content.value="✅ Đã copy vào clipboard"
        page.snack_bar.open = True
        page.update()
    copy_btn.on_click = do_copy

    speak_btn = ft.IconButton(
        icon=ft.Icons.VOLUME_UP, 
        tooltip="🔊 Đọc kết quả dịch",
        style=ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: ft.Colors.DEEP_ORANGE_600},
            bgcolor={ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, ft.Colors.DEEP_ORANGE)},
            overlay_color={ft.ControlState.PRESSED: ft.Colors.with_opacity(0.2, ft.Colors.DEEP_ORANGE)},
        )
    )

    def do_speak(e):
        nonlocal speaking
        
        # Nếu đang phát, thì dừng lại
        if speaking or is_speaking():
            stop_speaking()
            speaking = False
            speak_btn.icon = ft.Icons.VOLUME_UP
            speak_btn.tooltip = "🔊 Đọc kết quả dịch"
            page.snack_bar.content.value = "⏸️ Đã dừng đọc"
            page.snack_bar.open = True
            page.update()
            return
        
        # Nếu không có text thì không làm gì
        if not output_text.value or not output_text.value.strip():
            page.snack_bar.content.value = "⚠️ Chưa có kết quả dịch để đọc"
            page.snack_bar.open = True
            page.update()
            return
            
        # Bắt đầu phát
        try:
            speaking = True
            speak_btn.icon = ft.Icons.STOP
            speak_btn.tooltip = "⏸️ Dừng đọc"
            page.update()
            
            # Phát trong thread riêng để không block UI
            import threading
            def speak_thread():
                nonlocal speaking
                try:
                    speak(output_text.value, _lang_code(dst_lang.value))
                except Exception as ex:
                    page.snack_bar.content.value = f"❌ TTS lỗi: {ex}"
                    page.snack_bar.open = True
                finally:
                    speaking = False
                    speak_btn.icon = ft.Icons.VOLUME_UP
                    speak_btn.tooltip = "🔊 Đọc kết quả dịch"
                    page.update()
            
            threading.Thread(target=speak_thread, daemon=True).start()
            
        except Exception as ex:
            speaking = False
            speak_btn.icon = ft.Icons.VOLUME_UP
            speak_btn.tooltip = "🔊 Đọc kết quả dịch"
            page.snack_bar.content.value = f"❌ TTS lỗi: {ex}"
            page.snack_bar.open = True
            page.update()

    speak_btn.on_click = do_speak

    mic_btn = ft.IconButton(
        icon=ft.Icons.MIC, 
        tooltip="🎤 Ghi âm để dịch",
        style=ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: ft.Colors.RED_600},
            bgcolor={ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, ft.Colors.RED)},
            overlay_color={ft.ControlState.PRESSED: ft.Colors.with_opacity(0.2, ft.Colors.RED)},
        )
    )
    recording = False
    speaking = False
    realtime_translating = False
    record_spinner = ft.ProgressRing(
        width=20, 
        height=20, 
        visible=False, 
        color=ft.Colors.RED_600,
        stroke_width=3
    )
    # Biến để theo dõi trạng thái ghi âm
    recording_thread = None
    
    def stop_recording():
        nonlocal recording, recording_thread
        recording = False
        if recording_thread:
            recording_thread = None
        record_spinner.visible = False
        mic_btn.icon_color = None
        mic_btn.tooltip = "🎤 Ghi âm để dịch"
        page.update()

    def do_record(e):
        nonlocal recording, recording_thread
        
        if not recording:
            # Bắt đầu ghi âm
            recording = True
            record_spinner.visible = True
            mic_btn.icon_color = "red"
            mic_btn.tooltip = "🛑 Nhấn lại để dừng"
            page.snack_bar.content.value = "🎤 Đang ghi âm... Nhấn lại để dừng hoặc im lặng 2 giây"
            page.snack_bar.open = True
            page.update()
            
            def record_worker():
                nonlocal recording
                try:
                    import speech_recognition as sr
                    
                    # Khởi tạo recognizer
                    r = sr.Recognizer()
                    r.pause_threshold = 2.0  # Dừng sau 2 giây im lặng
                    r.timeout = 1.0  # Timeout cho việc bắt đầu nghe
                    r.phrase_time_limit = None  # Không giới hạn thời gian phrase
                    
                    with sr.Microphone() as source:
                        # Điều chỉnh nhiễu nền
                        r.adjust_for_ambient_noise(source, duration=0.5)
                        
                        # Kiểm tra nếu vẫn đang recording
                        if not recording:
                            return
                            
                        # Ghi âm với auto-stop sau 2 giây im lặng
                        audio = r.listen(source, timeout=30, phrase_time_limit=None)
                    
                    # Kiểm tra lại trạng thái recording
                    if not recording:
                        return
                    
                    # Xác định ngôn ngữ
                    src_code = _lang_code(src_lang.value)
                    if src_code == "auto":
                        src_code = "en"
                    
                    # Mapping cho Google Speech Recognition
                    lang_map = {
                        "vi": "vi-VN",
                        "en": "en-US", 
                        "zh": "zh-CN",
                        "ja": "ja-JP",
                        "ko": "ko-KR",
                        "fr": "fr-FR",
                        "de": "de-DE",
                        "es": "es-ES",
                        "it": "it-IT",
                        "pt": "pt-BR",
                        "ru": "ru-RU",
                        "ar": "ar-SA"
                    }
                    
                    recognition_lang = lang_map.get(src_code, "en-US")
                    
                    # Nhận dạng giọng nói
                    try:
                        text = r.recognize_google(audio, language=recognition_lang)
                        if text.strip():
                            input_text.value = text
                            page.snack_bar.content.value = f"✅ Đã chuyển đổi: {text[:40]}{'...' if len(text) > 40 else ''}"
                        else:
                            page.snack_bar.content.value = "⚠️ Không phát hiện được giọng nói rõ ràng"
                    
                    except sr.UnknownValueError:
                        page.snack_bar.content.value = "❌ Không thể nhận dạng giọng nói. Hãy thử nói rõ hơn."
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
                    stop_recording()
                    page.snack_bar.open = True
                    page.update()
            
            # Lưu reference thread và chạy
            recording_thread = page.run_thread(record_worker)
            
        else:
            # Dừng ghi âm thủ công
            page.snack_bar.content.value = "⏹️ Đã dừng ghi âm thủ công"
            page.snack_bar.open = True
            stop_recording()
    
    mic_btn.on_click = do_record

    # -------------------- Translate --------------------
    prog = ft.ProgressBar(
        visible=False, 
        color=ft.Colors.BLUE_600, 
        bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.BLUE),
        height=3,
        border_radius=2,
    )
    loading_ring = ft.ProgressRing(
        width=16, 
        height=16, 
        visible=False, 
        color=ft.Colors.BLUE_600,
        stroke_width=2
    )

    # Nút dịch ban đầu
    translate_btn = ft.ElevatedButton(
        text="Dịch",
        disabled=False,
        height=45,
        width=100,  # Đặt width cố định để tránh lấn khi text thay đổi
        visible=True,
        animate_opacity=300,  # Smooth transition khi ẩn/hiện
        style=ft.ButtonStyle(
            color={
                ft.ControlState.DEFAULT: ft.Colors.WHITE,
                ft.ControlState.DISABLED: ft.Colors.GREY_400,
            },
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.BLUE_600,
                ft.ControlState.HOVERED: ft.Colors.BLUE_700,
                ft.ControlState.PRESSED: ft.Colors.BLUE_800,
                ft.ControlState.DISABLED: ft.Colors.GREY_300,
            },
            elevation={ft.ControlState.DEFAULT: 2, ft.ControlState.HOVERED: 4},
            shape=ft.RoundedRectangleBorder(radius=8),
        )
    )

    def do_translate(e):
        nonlocal src_lang, dst_lang, use_context

        text = (input_text.value or "").strip()
        if not text:
            page.snack_bar.content.value = "Vui lòng nhập nội dung"
            page.snack_bar.open = True
            page.update()
            return

        src_code = _lang_code(src_lang.value)
        dst_code = _lang_code(dst_lang.value)
        domain = domain_dd.value if use_context.value else None

        # Khi bắt đầu dịch
        translate_btn.text = "⏳ Dịch"
        translate_btn.disabled = True
        loading_ring.visible = True
        prog.visible = True
        page.update()

        def worker():
            nonlocal text
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
                items = get_history()
                if items:
                    recent_items = items[:5] if len(items) >= 5 else items
                    history_text = ""
                    
                    for i, (src, dst, text_in, text_out, ctx, created) in enumerate(recent_items, 1):
                        history_text += f"🔹 {created} | {src} → {dst}\n"
                        history_text += f"📝 Đầu vào: {text_in[:50]}{'...' if len(text_in) > 50 else ''}\n"
                        history_text += f"✨ Kết quả: {text_out[:50]}{'...' if len(text_out) > 50 else ''}\n"
                        if ctx:
                            history_text += f"🏷️ Ngữ cảnh: {ctx}\n"
                        history_text += "─" * 50 + "\n\n"
                    
                    last_history.value = history_text.strip()
                    last_history.color = get_history_text_color()
            
            # Khi hoàn tất → trả lại trạng thái nút ban đầu (luôn thực hiện)
            output_text.value = result
            translate_btn.text = "Dịch"
            translate_btn.disabled = False
            loading_ring.visible = False
            prog.visible = False
            page.update()

        page.run_thread(worker)

    translate_btn.on_click = do_translate

    # -------------------- History --------------------
    history_btn = ft.IconButton(
        icon=ft.Icons.HISTORY, 
        tooltip="📜 Xem lịch sử dịch",
        style=ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: ft.Colors.BROWN_600},
            bgcolor={ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, ft.Colors.BROWN)},
            overlay_color={ft.ControlState.PRESSED: ft.Colors.with_opacity(0.2, ft.Colors.BROWN)},
        )
    )
    def show_history(e):
        # Toggle hiển thị history container
        if history_container.visible:
            # Nếu đang hiển thị thì ẩn đi
            history_container.visible = False
        else:
            # Nếu đang ẩn thì hiển thị và cập nhật nội dung
            items = get_history()
            if not items:
                page.snack_bar.content.value = "Chưa có lịch sử dịch"
                page.snack_bar.open = True
                page.update()
                return
            
            # Hiển thị 5 lịch sử gần nhất
            recent_items = items[:5] if len(items) >= 5 else items
            history_text = ""
            
            for i, (src, dst, text_in, text_out, ctx, created) in enumerate(recent_items, 1):
                history_text += f"🔹 {created} | {src} → {dst}\n"
                history_text += f"📝 Đầu vào: {text_in[:50]}{'...' if len(text_in) > 50 else ''}\n"
                history_text += f"✨ Kết quả: {text_out[:50]}{'...' if len(text_out) > 50 else ''}\n"
                if ctx:
                    history_text += f"🏷️ Ngữ cảnh: {ctx}\n"
                history_text += "─" * 50 + "\n\n"
            
            last_history.value = history_text.strip()
            last_history.color = get_history_text_color()
            history_container.visible = True
        
        page.update()
    history_btn.on_click = show_history

    # -------------------- Layout --------------------

    # Controls container
    controls_card = ft.Container(
        content=ft.Column([
            ft.Row([
                src_lang, 
                ft.Container(swap_btn, margin=ft.margin.only(top=15)), 
                dst_lang
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            ft.Row([
                file_btn, img_btn, mic_btn, record_spinner, 
                ft.Container(width=20),  # Spacer
                history_btn, theme_btn
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
        ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.padding.all(25),
        margin=ft.margin.only(top=10, bottom=20),
        bgcolor=get_container_bgcolor(
            ft.Colors.with_opacity(0.8, ft.Colors.WHITE),
            ft.Colors.with_opacity(0.3, ft.Colors.BLUE_GREY_800)
        ),
        border=ft.border.all(1, ft.Colors.with_opacity(0.4, ft.Colors.BLUE_GREY)),
        border_radius=15,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
        animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT)
    )

    # Input text container
    input_container = ft.Container(
        content=ft.Column([
            ft.Text("Văn bản đầu vào", size=18, weight=ft.FontWeight.BOLD, color=get_border_color(ft.Colors.BLUE_600)),
            input_text,
        ], spacing=10),
        padding=ft.padding.all(20),
        margin=ft.margin.only(bottom=15),
        bgcolor=get_container_bgcolor(
            ft.Colors.with_opacity(0.6, ft.Colors.BLUE_50),
            ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_900)
        ),
        border=ft.border.all(1, ft.Colors.with_opacity(0.4, ft.Colors.BLUE)),
        border_radius=15,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=5,
            color=ft.Colors.with_opacity(0.05, ft.Colors.BLUE),
            offset=ft.Offset(0, 2),
        ),
        animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT)
    )

    # Context and translate section
    action_container = ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Row([use_context, domain_dd], spacing=20),
                expand=True
            ),
            ft.Container(
                content=ft.Column([
                    ft.Row([realtime_toggle_container, realtime_indicator, loading_ring, translate_btn], spacing=8, alignment=ft.MainAxisAlignment.END),
                    prog
                ], spacing=8),
                width=340
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.padding.all(20),
        margin=ft.margin.only(bottom=15),
        bgcolor=get_container_bgcolor(
            ft.Colors.with_opacity(0.6, ft.Colors.TEAL_50),
            ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_900)
        ),
        border=ft.border.all(1, ft.Colors.with_opacity(0.4, ft.Colors.TEAL)),
        border_radius=15,
        animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT)
    )

    # Output text container
    output_container = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("Kết quả dịch", size=18, weight=ft.FontWeight.BOLD, color=get_border_color(ft.Colors.GREEN_600)),
                ft.Row([copy_btn, speak_btn], spacing=10),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            output_text,
        ], spacing=10),
        padding=ft.padding.all(20),
        margin=ft.margin.only(bottom=15),
        bgcolor=get_container_bgcolor(
            ft.Colors.with_opacity(0.6, ft.Colors.GREEN_50),
            ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_900)
        ),
        border=ft.border.all(1, ft.Colors.with_opacity(0.4, ft.Colors.GREEN)),
        border_radius=15,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=5,
            color=ft.Colors.with_opacity(0.05, ft.Colors.GREEN),
            offset=ft.Offset(0, 2),
        ),
        animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT)
    )



    def clear_history_action(e):
        import sqlite3
        conn = sqlite3.connect("history.db")
        conn.execute("DELETE FROM history")
        conn.commit()
        conn.close()
        last_history.value = ""
        history_container.visible = False
        page.snack_bar.content.value = "Đã xóa toàn bộ lịch sử"
        page.snack_bar.open = True
        page.update()

    def export_history_action(e):
        items = get_history()
        if not items:
            page.snack_bar.content.value = "Không có lịch sử để xuất"
            page.snack_bar.open = True
            page.update()
            return
            
        with open("history_export.txt", "w", encoding="utf-8") as f:
            for src, dst, text_in, text_out, ctx, created in items:
                f.write(f"{created} | {src} → {dst} ({ctx or 'Không có ngữ cảnh'})\n")
                f.write(f"Đầu vào: {text_in}\n")
                f.write(f"Kết quả: {text_out}\n\n")
        page.snack_bar.content.value = "Đã xuất ra file history_export.txt"
        page.snack_bar.open = True
        page.update()

    history_actions = ft.Row([
        ft.TextButton("Xuất lịch sử", on_click=export_history_action),
        ft.TextButton("Xóa lịch sử", on_click=clear_history_action),
        ft.TextButton("Ẩn", on_click=lambda e: setattr(history_container, 'visible', False) or page.update()),
    ], alignment=ft.MainAxisAlignment.END, spacing=10)

    # History container - ẩn ban đầu
    history_container = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("Lịch sử gần nhất", size=16, weight=ft.FontWeight.BOLD, color=get_text_color()),
                history_actions,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            last_history,
        ], spacing=8),
        padding=ft.padding.all(15),
        bgcolor=get_container_bgcolor(
            ft.Colors.with_opacity(0.4, ft.Colors.GREY_100),
            ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_900)
        ),
        border=ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.BLUE_GREY)),
        border_radius=10,
        visible=False,  # Ẩn ban đầu
        animate_opacity=300,
        animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT)
    )

    # Main container
    main_container = ft.Container(
        content=ft.Column([
            controls_card,
            input_container,
            action_container,
            output_container,
            history_container,
        ], spacing=0),
        padding=ft.padding.all(20),
        expand=True,
    )

    page.add(main_container)
    page.overlay.append(page.snack_bar)
    page.horizontal_alignment = "stretch"
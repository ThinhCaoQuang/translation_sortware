import flet as ft
from api import CONTEXTS
from languages import LANGUAGES
from history import init_db
from handlers import (
    AppState, ThemeHandler, TranslationHandler, FileHandler, 
    AudioHandler, HistoryHandler, UtilityHandler
)


def main(page: ft.Page):
    """Hàm chính khởi tạo giao diện ứng dụng"""
    # ==================== CẤU HÌNH TRANG CHÍNH ====================
    page.title = "🌐 Translation App"
    page.theme_mode = "dark"
    page.window_maximized = True    
    page.padding = 0
    page.vertical_alignment = "start"
    page.scroll = "adaptive"
    
    page.bgcolor = ThemeHandler.get_page_bgcolor(page)
    
    # Cấu hình snackbar
    snackbar_colors = ThemeHandler.get_snackbar_colors(page)
    page.snack_bar = ft.SnackBar(
        content=ft.Text("", color=snackbar_colors["content_color"]),
        bgcolor=snackbar_colors["bgcolor"],
        duration=3000,
        margin=ft.margin.all(10),
        behavior=ft.SnackBarBehavior.FLOATING
    )
    # Khởi tạo database
    init_db()
    
    # ==================== KHỞI TẠO STATE VÀ HANDLERS ====================
    app_state = AppState()
    translation_handler = TranslationHandler(app_state)
    audio_handler = AudioHandler(app_state)
    
    
    # ==================== TẠO CÁC CONTROL CHÍNH ====================
    
    # Dropdown ngôn ngữ nguồn
    src_lang = ft.Dropdown(
        label="Ngôn ngữ nguồn",
        options=[ft.dropdown.Option(lang) for lang in LANGUAGES.keys()],
        value="Auto Detect",
        width=330,
        border_color=ThemeHandler.get_border_color(page, ft.Colors.BLUE_400),
        focused_border_color=ThemeHandler.get_border_color(page, ft.Colors.BLUE_600),
        bgcolor=ThemeHandler.get_dropdown_bgcolor(page),
        content_padding=ft.padding.symmetric(horizontal=15, vertical=12),
        text_style=ft.TextStyle(size=14),
    )

    # Dropdown ngôn ngữ đích
    dst_lang = ft.Dropdown(
        label="Ngôn ngữ đích",
        options=[ft.dropdown.Option(lang) for lang in LANGUAGES.keys()],
        value="Tiếng Việt",
        width=330,
        border_color=ThemeHandler.get_border_color(page, ft.Colors.GREEN_400),
        focused_border_color=ThemeHandler.get_border_color(page, ft.Colors.GREEN_600),
        bgcolor=ThemeHandler.get_dropdown_bgcolor(page),
        content_padding=ft.padding.symmetric(horizontal=15, vertical=12),
        text_style=ft.TextStyle(size=14),
    )

    # Nút chuyển đổi theme
    theme_btn = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE, 
        tooltip="🌓 Chuyển chế độ nền",
        style=ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: ft.Colors.AMBER_600},
            bgcolor={ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, ft.Colors.AMBER)},
            overlay_color={ft.ControlState.PRESSED: ft.Colors.with_opacity(0.2, ft.Colors.AMBER)},
        )
    )
    
    # Nút đổi chiều ngôn ngữ
    swap_btn = ft.IconButton(
        icon=ft.Icons.SWAP_HORIZ, 
        tooltip="🔄 Đổi chiều ngôn ngữ",
        style=ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: ft.Colors.PURPLE_600},
            bgcolor={ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, ft.Colors.PURPLE)},
            overlay_color={ft.ControlState.PRESSED: ft.Colors.with_opacity(0.2, ft.Colors.PURPLE)},
        ),
        on_click=lambda e: UtilityHandler.do_swap(e, page, src_lang, dst_lang)
    )
# ==================== TEXT FIELDS ====================
    
    # Trường nhập text
    input_text = ft.TextField(
        label="Nhập văn bản cần dịch",
        multiline=True,
        min_lines=5,
        max_lines=10,
        expand=True,
        border_color=ThemeHandler.get_border_color(page, ft.Colors.BLUE_400),
        focused_border_color=ThemeHandler.get_border_color(page, ft.Colors.BLUE_600),
        bgcolor=ThemeHandler.get_textfield_bgcolor(page),
        content_padding=ft.padding.all(15),
        text_style=ft.TextStyle(size=16),
    )
    
    # Trường hiển thị kết quả
    output_text = ft.TextField(
        label="Kết quả dịch",
        multiline=True,
        min_lines=5,
        max_lines=10,
        expand=True,
        read_only=True,
        border_color=ThemeHandler.get_border_color(page, ft.Colors.GREEN_400),
        focused_border_color=ThemeHandler.get_border_color(page, ft.Colors.GREEN_600),
        bgcolor=ThemeHandler.get_textfield_bgcolor(page),
        content_padding=ft.padding.all(15),
        text_style=ft.TextStyle(size=16, weight=ft.FontWeight.W_500),
    )
    
    # Text hiển thị lịch sử
    last_history = ft.Text(
        "", 
        selectable=True, 
        size=14, 
        color=ThemeHandler.get_history_text_color(page),
        style=ft.TextStyle(weight=ft.FontWeight.W_400)
    )

# ==================== CONTEXT/DOMAIN CONTROLS ====================
    
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
        border_color=ThemeHandler.get_border_color(page, ft.Colors.TEAL_400),
        focused_border_color=ThemeHandler.get_border_color(page, ft.Colors.TEAL_600),
        bgcolor=ThemeHandler.get_dropdown_bgcolor(page),
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
        text_style=ft.TextStyle(size=14),
    )
    
    use_context.on_change = lambda e: UtilityHandler.toggle_context(e, page, domain_dd, use_context)
    # ==================== FILE PICKERS ====================
    
    pick_txt = ft.FilePicker()
    pick_img = ft.FilePicker()
    page.overlay.append(pick_txt)
    page.overlay.append(pick_img)
    
    # ==================== BUTTONS ====================
    
    # Nút upload file
    file_btn = ft.IconButton(
        icon=ft.Icons.UPLOAD_FILE,
        tooltip="📄 Mở file .txt/.docx",
        on_click=lambda e: pick_txt.pick_files(
            allow_multiple=False, 
            allowed_extensions=["txt", "docx"]
        ),
        style=ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: ft.Colors.INDIGO_600},
            bgcolor={ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, ft.Colors.INDIGO)},
            overlay_color={ft.ControlState.PRESSED: ft.Colors.with_opacity(0.2, ft.Colors.INDIGO)},
        )
    )

    # Nút OCR từ ảnh
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
# Nút copy
    copy_btn = ft.IconButton(
        icon=ft.Icons.CONTENT_COPY, 
        tooltip="📋 Copy kết quả",
        style=ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: ft.Colors.CYAN_600},
            bgcolor={ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, ft.Colors.CYAN)},
            overlay_color={ft.ControlState.PRESSED: ft.Colors.with_opacity(0.2, ft.Colors.CYAN)},
        ),
        on_click=lambda e: UtilityHandler.do_copy(e, page, output_text)
    )
    
    # Nút text-to-speech
    speak_btn = ft.IconButton(
        icon=ft.Icons.VOLUME_UP, 
        tooltip="🔊 Đọc kết quả dịch",
        style=ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: ft.Colors.DEEP_ORANGE_600},
            bgcolor={ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, ft.Colors.DEEP_ORANGE)},
            overlay_color={ft.ControlState.PRESSED: ft.Colors.with_opacity(0.2, ft.Colors.DEEP_ORANGE)},
        )
    )
    # Nút ghi âm
    mic_btn = ft.IconButton(
        icon=ft.Icons.MIC, 
        tooltip="🎤 Ghi âm để dịch",
        style=ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: ft.Colors.RED_600},
            bgcolor={ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, ft.Colors.RED)},
            overlay_color={ft.ControlState.PRESSED: ft.Colors.with_opacity(0.2, ft.Colors.RED)},
        )
    )
    
    record_spinner = ft.ProgressRing(
        width=20, 
        height=20, 
        visible=False, 
        color=ft.Colors.RED_600,
        stroke_width=3
    )

# Nút lịch sử
    history_btn = ft.IconButton(
        icon=ft.Icons.HISTORY, 
        tooltip="📜 Xem lịch sử dịch",
        style=ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: ft.Colors.BROWN_600},
            bgcolor={ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, ft.Colors.BROWN)},
            overlay_color={ft.ControlState.PRESSED: ft.Colors.with_opacity(0.2, ft.Colors.BROWN)},
        )
    )
    
    # ==================== HISTORY ACTIONS ====================
    
    history_actions = ft.Row([
        ft.TextButton("Xuất lịch sử", on_click=lambda e: HistoryHandler.export_history_action(e, page)),
        ft.TextButton("Xóa lịch sử", on_click=lambda e: HistoryHandler.clear_history_action(e, page, last_history, history_container)),
        ft.TextButton("Ẩn", on_click=lambda e: setattr(history_container, 'visible', False) or page.update()),
    ], alignment=ft.MainAxisAlignment.END, spacing=10)
    
    # ==================== LAYOUT CONTAINERS ====================
    
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
        bgcolor=ThemeHandler.get_container_bgcolor(page,
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
    
    # ==================== PROGRESS & LOADING ====================
    
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
    
    # ==================== REALTIME CONTROLS ====================
    
    # Toggle switch cho realtime - ẩn vì luôn bật
    realtime_switch = ft.Switch(
        value=True,  # Bật mặc định
        active_color=ft.Colors.GREEN_600,
        inactive_thumb_color=ft.Colors.GREY_400,
        inactive_track_color=ft.Colors.GREY_300,
        visible=False,  # Ẩn switch
    )

    realtime_toggle_container = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.AUTORENEW, size=16, color=ft.Colors.GREEN_600),
            ft.Text("Dịch tự động", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.GREEN_600),
        ], spacing=8, alignment=ft.MainAxisAlignment.END),
        padding=ft.padding.symmetric(horizontal=8, vertical=4),
        border_radius=8,
        visible=True,  # Luôn hiển thị thông báo
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
    
    # Nút dịch thủ công - ẩn vì dùng realtime
    translate_btn = ft.ElevatedButton(
        text="Dịch",
        disabled=False,
        height=45,
        width=100,
        visible=False,  # Ẩn nút dịch thủ công
        animate_opacity=300,
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

    # ==================== THIẾT LẬP EVENT HANDLERS ====================
    
    def toggle_theme(e):
        """Xử lý chuyển đổi theme"""
        page.theme_mode = "light" if page.theme_mode == "dark" else "dark"
        theme_btn.icon = ft.Icons.DARK_MODE if page.theme_mode == "light" else ft.Icons.LIGHT_MODE
        
        # Cập nhật màu nền trang
        page.bgcolor = ThemeHandler.get_page_bgcolor(page)
        
        # Cập nhật snackbar
        snackbar_colors = ThemeHandler.get_snackbar_colors(page)
        page.snack_bar.content.color = snackbar_colors["content_color"]
        page.snack_bar.bgcolor = snackbar_colors["bgcolor"]
        
        # Cập nhật màu nền dropdowns và textfields
        dropdown_bg = ThemeHandler.get_dropdown_bgcolor(page)
        src_lang.bgcolor = dropdown_bg
        dst_lang.bgcolor = dropdown_bg
        domain_dd.bgcolor = dropdown_bg
        
        # Cập nhật border colors cho dropdowns
        src_lang.border_color = ThemeHandler.get_border_color(page, ft.Colors.BLUE_400)
        src_lang.focused_border_color = ThemeHandler.get_border_color(page, ft.Colors.BLUE_600)
        dst_lang.border_color = ThemeHandler.get_border_color(page, ft.Colors.GREEN_400)
        dst_lang.focused_border_color = ThemeHandler.get_border_color(page, ft.Colors.GREEN_600)
        domain_dd.border_color = ThemeHandler.get_border_color(page, ft.Colors.TEAL_400)
        domain_dd.focused_border_color = ThemeHandler.get_border_color(page, ft.Colors.TEAL_600)
        
        textfield_bg = ThemeHandler.get_textfield_bgcolor(page)
        input_text.bgcolor = textfield_bg
        output_text.bgcolor = textfield_bg
        
        # Cập nhật border colors cho textfields
        input_text.border_color = ThemeHandler.get_border_color(page, ft.Colors.BLUE_400)
        input_text.focused_border_color = ThemeHandler.get_border_color(page, ft.Colors.BLUE_600)
        output_text.border_color = ThemeHandler.get_border_color(page, ft.Colors.GREEN_400)
        output_text.focused_border_color = ThemeHandler.get_border_color(page, ft.Colors.GREEN_600)
        
        # Cập nhật màu containers
        controls_card.bgcolor = ThemeHandler.get_container_bgcolor(page,
            ft.Colors.with_opacity(0.8, ft.Colors.WHITE),
            ft.Colors.with_opacity(0.3, ft.Colors.BLUE_GREY_800)
        )
        
        input_container.bgcolor = ThemeHandler.get_container_bgcolor(page,
            ft.Colors.with_opacity(0.6, ft.Colors.BLUE_50),
            ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_900)
        )
        
        action_container.bgcolor = ThemeHandler.get_container_bgcolor(page,
            ft.Colors.with_opacity(0.6, ft.Colors.TEAL_50),
            ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_900)
        )
        
        output_container.bgcolor = ThemeHandler.get_container_bgcolor(page,
            ft.Colors.with_opacity(0.6, ft.Colors.GREEN_50),
            ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_900)
        )
        
        history_container.bgcolor = ThemeHandler.get_container_bgcolor(page,
            ft.Colors.with_opacity(0.4, ft.Colors.GREY_100),
            ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_900)
        )
        
        # Cập nhật text colors cho section headers
        input_header = input_container.content.controls[0]
        output_header = output_container.content.controls[0].controls[0]
        
        input_header.color = ThemeHandler.get_border_color(page, ft.Colors.BLUE_600)
        output_header.color = ThemeHandler.get_border_color(page, ft.Colors.GREEN_600)
        
        # Cập nhật history header và text nếu đang hiển thị
        if history_container.visible:
            history_header = history_container.content.controls[0].controls[0]
            history_header.color = ThemeHandler.get_text_color(page)
            
        # Cập nhật màu text của lịch sử
        last_history.color = ThemeHandler.get_history_text_color(page)
        
        # Cập nhật màu cho toggle realtime
        is_dark = page.theme_mode == "dark"
        toggle_icon = realtime_toggle_container.content.controls[0]
        toggle_text = realtime_toggle_container.content.controls[1]
        toggle_icon.color = ft.Colors.BLUE_400 if is_dark else ft.Colors.BLUE_600
        toggle_text.color = ft.Colors.WHITE70 if is_dark else ft.Colors.BLACK87
        
        page.update()
    
    theme_btn.on_click = toggle_theme
    # Realtime đã được bật mặc định trong AppState, chỉ cần setup input handler
    input_text.on_change = lambda e: translation_handler.on_input_change(
        e, page, input_text, output_text, prog, src_lang, dst_lang, 
        domain_dd, use_context, history_container, last_history
    )
    
    translate_btn.on_click = lambda e: translation_handler.do_translate(
        e, page, input_text, output_text, src_lang, dst_lang, domain_dd, 
        use_context, translate_btn, loading_ring, prog, history_container, last_history
    )
    
    pick_txt.on_result = lambda e: FileHandler.on_pick_txt(e, input_text, page)
    
    # Định nghĩa callback cho auto-translate sau OCR
    def auto_translate_callback(e):
        if app_state.realtime_enabled:
            translation_handler.do_translate(
                e, page, input_text, output_text, src_lang, dst_lang, domain_dd, 
                use_context, translate_btn, loading_ring, prog, history_container, last_history
            )
    
    pick_img.on_result = lambda e: FileHandler.on_pick_image(
        e, input_text, img_btn, page, src_lang, app_state.realtime_enabled, auto_translate_callback
    )
    
    speak_btn.on_click = lambda e: audio_handler.do_speak(
        e, page, output_text, speak_btn, dst_lang
    )
    
    mic_btn.on_click = lambda e: audio_handler.do_record(
        e, page, input_text, mic_btn, record_spinner, src_lang
    )
    
    history_btn.on_click = lambda e: HistoryHandler.show_history(
        e, page, history_container, last_history
    )
    # Input text container
    input_container = ft.Container(
        content=ft.Column([
            ft.Text("Văn bản đầu vào", size=18, weight=ft.FontWeight.BOLD, 
                   color=ThemeHandler.get_border_color(page, ft.Colors.BLUE_600)),
            input_text,
        ], spacing=10),
        padding=ft.padding.all(20),
        margin=ft.margin.only(bottom=15),
        bgcolor=ThemeHandler.get_container_bgcolor(page,
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
                    ft.Row([realtime_toggle_container, loading_ring], 
                          spacing=8, alignment=ft.MainAxisAlignment.END),
                    prog
                ], spacing=8),
                width=250  # Giảm width vì ít control hơn
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.padding.all(20),
        margin=ft.margin.only(bottom=15),
        bgcolor=ThemeHandler.get_container_bgcolor(page,
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
                ft.Text("Kết quả dịch", size=18, weight=ft.FontWeight.BOLD, 
                       color=ThemeHandler.get_border_color(page, ft.Colors.GREEN_600)),
                ft.Row([copy_btn, speak_btn], spacing=10),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            output_text,
        ], spacing=10),
        padding=ft.padding.all(20),
        margin=ft.margin.only(bottom=15),
        bgcolor=ThemeHandler.get_container_bgcolor(page,
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
    # History container - ẩn ban đầu
    history_container = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("Lịch sử gần nhất", size=16, weight=ft.FontWeight.BOLD, 
                       color=ThemeHandler.get_text_color(page)),
                history_actions,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            last_history,
        ], spacing=8),
        padding=ft.padding.all(15),
        bgcolor=ThemeHandler.get_container_bgcolor(page,
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

    # ==================== THÊM VÀO TRANG ====================
    page.add(main_container)
    page.overlay.append(page.snack_bar)
    page.horizontal_alignment = "stretch"


if __name__ == "__main__":
    import flet as ft
    ft.app(target=main)

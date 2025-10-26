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

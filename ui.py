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

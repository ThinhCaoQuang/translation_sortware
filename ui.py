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
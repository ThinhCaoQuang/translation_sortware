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
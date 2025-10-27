import flet as ft


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

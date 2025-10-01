import flet as ft

def main(page: ft.Page):
    page.title = "Phần mềm dịch thuật"
    page.theme_mode = "dark"
    page.padding = 20
    page.vertical_alignment = "start"

    # Dropdown chọn ngôn ngữ
    src_lang = ft.Dropdown(
        label="Ngôn ngữ nguồn",
        options=[
            ft.dropdown.Option("Tiếng Việt"),
            ft.dropdown.Option("Tiếng Anh"),
            ft.dropdown.Option("Tiếng Nhật"),
        ],
        value="Tiếng Việt",
        width=150,
    )

    dst_lang = ft.Dropdown(
        label="Ngôn ngữ đích",
        options=[
            ft.dropdown.Option("Tiếng Việt"),
            ft.dropdown.Option("Tiếng Anh"),
            ft.dropdown.Option("Tiếng Nhật"),
        ],
        value="Tiếng Anh",
        width=150,
    )
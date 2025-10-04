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
    # Nút chức năng (dùng string icon thay vì flet.icons)
        swap_btn = ft.IconButton(icon="compare_arrows", tooltip="Đổi chiều")
        file_btn = ft.IconButton(icon="upload_file", tooltip="Tải file")
        img_btn = ft.IconButton(icon="image", tooltip="Tải ảnh")

    # Công cụ copy & đọc
        copy_btn = ft.IconButton(icon="content_copy", tooltip="Copy")
        speak_btn = ft.IconButton(icon="volume_up", tooltip="Đọc")
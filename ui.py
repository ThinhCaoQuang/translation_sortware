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

    # Nút chức năng
    swap_btn = ft.IconButton(icon="compare_arrows", tooltip="Đổi chiều")
    file_btn = ft.IconButton(icon="upload_file", tooltip="Tải file")
    img_btn = ft.IconButton(icon="image", tooltip="Tải ảnh")

    # Công cụ copy & đọc
    copy_btn = ft.IconButton(icon="content_copy", tooltip="Copy")
    speak_btn = ft.IconButton(icon="volume_up", tooltip="Đọc")

    # Input text có nút micro
    input_text = ft.TextField(
        label="Nhập văn bản",
        multiline=True,
        min_lines=5,
        max_lines=10,
        expand=True,
        suffix=ft.IconButton(icon="mic", tooltip="Ghi âm"),
    )

    # Output
    output_text = ft.TextField(
        label="Kết quả dịch",
        multiline=True,
        min_lines=5,
        max_lines=10,
        expand=True,
        read_only=True,
    )

    # Thêm checkbox và nút dịch
    context_check = ft.Checkbox(label="Dịch theo ngữ cảnh")
    translate_btn = ft.ElevatedButton(text="Dịch")

    # Layout
    page.add(
        ft.Row([src_lang, swap_btn, dst_lang, file_btn, img_btn], alignment="start"),
        input_text,
        ft.Row([context_check, translate_btn], alignment="spaceBetween"),
        output_text,
        ft.Row([copy_btn, speak_btn], alignment="end"),
    )

# Chạy app
ft.app(target=main)

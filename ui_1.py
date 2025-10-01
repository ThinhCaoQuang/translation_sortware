import flet as ft

def main(page: ft.Page):
    page.title = "Phần mềm dịch thuật"
    page.bgcolor = "white"
    page.padding = 20

    # Nhãn nhập văn bản
    input_label = ft.Text("Nhập văn bản:", size=16, color="black")
    input_box = ft.TextField(multiline=True, min_lines=5, max_lines=10, width=600)

    # Nút dịch
    translate_button = ft.ElevatedButton(
        text="Dịch",
        icon="translate",
        bgcolor="blue",
        color="white"
    )

    # Ô kết quả
    output_label = ft.Text("Kết quả dịch:", size=16, color="black")
    output_box = ft.TextField(multiline=True, min_lines=5, max_lines=10, width=600, read_only=True)

    # Sắp xếp layout
    page.add(
        input_label,
        input_box,
        translate_button,
        output_label,
        output_box
    )

ft.app(target=main)

import flet as ft
from docx import Document
from api import translate_text, LANGUAGES, CONTEXTS
from text_to_speech import speak
from speech_to_text import transcribe_audio
from languages import LANGUAGES
from history import init_db, add_history, get_history


def _lang_code(display: str) -> str:
    return LANGUAGES.get(display, "auto")


def main(page: ft.Page):
    page.title = "Phần mềm dịch thuật"
    page.theme_mode = "dark"
    page.padding = 20
    page.vertical_alignment = "start"
    page.scroll = "adaptive"
    page.snack_bar = ft.SnackBar(content=ft.Text(""), duration=3000)
    init_db()

    # -------------------- Language controls --------------------
    src_lang = ft.Dropdown(
        label="Ngôn ngữ nguồn",
        options=[ft.dropdown.Option(lang) for lang in LANGUAGES.keys()],
        value="Auto Detect",
        width=330,
    )

    dst_lang = ft.Dropdown(
        label="Ngôn ngữ đích",
        options=[ft.dropdown.Option(lang) for lang in LANGUAGES.keys()],
        value="Tiếng Việt",
        width=330,
    )

    swap_btn = ft.IconButton(icon=ft.Icons.SWAP_HORIZ, tooltip="Đổi chiều")

    def do_swap(e):
        s, d = src_lang.value, dst_lang.value
        src_lang.value, dst_lang.value = d, s
        page.update()
    swap_btn.on_click = do_swap

    # -------------------- Text fields --------------------
    input_text = ft.TextField(
        label="Nhập văn bản",
        multiline=True,
        min_lines=5,
        max_lines=10,
        expand=True,
    )
    def on_input_change(e):
        if not input_text.value.strip():
            output_text.value = ""
            page.update()
    input_text.on_change = on_input_change

    output_text = ft.TextField(
        label="Kết quả dịch",
        multiline=True,
        min_lines=5,
        max_lines=10,
        expand=True,
        read_only=True,
    )

    # -------------------- Context / Domain --------------------
    use_context = ft.Checkbox(label="Dịch theo ngữ cảnh")
    domain_dd = ft.Dropdown(
        label="Ngữ cảnh",
        options=[ft.dropdown.Option(x) for x in CONTEXTS],
        value="Daily",
        width=300,
    )

    # -------------------- File pickers --------------------
    pick_txt = ft.FilePicker()
    pick_img = ft.FilePicker()
    page.overlay.append(pick_txt)
    page.overlay.append(pick_img)

    def on_pick_txt(e: ft.FilePickerResultEvent):
        if e.files:
            p = e.files[0].path
            try:
                if p.endswith(".docx"):
                    doc = Document(p)
                    input_text.value = "\n".join([para.text for para in doc.paragraphs])
                else:
                    with open(p, "r", encoding="utf-8", errors="ignore") as rf:
                        input_text.value = rf.read()
            except Exception as ex:
                input_text.value = f"[Lỗi đọc file: {ex}]"
        page.update()
    pick_txt.on_result = on_pick_txt

    def on_pick_image(e: ft.FilePickerResultEvent):
        if e.files:
            from PIL import Image
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        img_path = e.files[0].path
        try:
            img = Image.open(img_path)
            src_code = _lang_code(src_lang.value)
            lang_code = {
                "vi": "vie",
                "en": "eng"
            }.get(src_code, "eng")  # fallback nếu không rõ
            if src_lang.value == "Auto Detect":
                ocr_lang = "vie+eng"
                page.snack_bar.content.value = "Ảnh có nhiều ngôn ngữ, đang dùng OCR: vie+eng"
                page.snack_bar.open = True
                page.update()
            else:
                ocr_lang = lang_code
            text = pytesseract.image_to_string(img, lang=ocr_lang)
            input_text.value = text
            page.snack_bar.content.value = "Đã trích xuất chữ từ ảnh"
            page.snack_bar.open = True
            page.update()
        except Exception as ex:
            input_text.value = f"[Lỗi OCR: {ex}]"
        page.update()

    pick_img.on_result = on_pick_image

    file_btn = ft.IconButton(
        icon=ft.Icons.UPLOAD_FILE,
        tooltip="Mở .txt/ .docx",
        on_click=lambda e: pick_txt.pick_files(allow_multiple=False, allowed_extensions=["txt", "docx"]),
    )
    img_btn = ft.IconButton(
        icon=ft.Icons.IMAGE,
        tooltip="Mở ảnh",
        on_click=lambda e: pick_img.pick_files(allow_multiple=False, allowed_extensions=["jpg", "png", "jpeg"]),
    )

    # -------------------- Copy / Speak --------------------
    copy_btn = ft.IconButton(icon=ft.Icons.CONTENT_COPY, tooltip="Copy")

    def do_copy(e):
        page.set_clipboard(output_text.value or "")
        page.snack_bar.content.value="Đã copy vào clipboard"
        page.snack_bar.open = True
        page.update()
    copy_btn.on_click = do_copy

    speak_btn = ft.IconButton(icon=ft.Icons.VOLUME_UP, tooltip="Đọc")

    def do_speak(e):
        try:
            speak(output_text.value or "", _lang_code(dst_lang.value))
        except Exception as ex:
            page.snack_bar.content.value = f"TTS lỗi: {ex}"
            page.snack_bar.open = True
            page.update()

    speak_btn.on_click = do_speak

    mic_btn = ft.IconButton(icon=ft.Icons.MIC, tooltip="Ghi âm")

    def do_record(e):
        try:
            text = transcribe_audio(lang="vi-VN")
            input_text.value = text
            page.update()
        except Exception as ex:
            page.snack_bar.content.value = "Lỗi ghi âm: {ex}"
            page.snack_bar.open = True
            page.update()

    mic_btn.on_click = do_record

    # -------------------- Translate --------------------
    prog = ft.ProgressBar(visible=False)
    translate_btn = ft.ElevatedButton(text="Dịch")

    def do_translate(e):
        text = (input_text.value or "").strip()
        if not text:
            page.snack_bar.content.value = "Vui lòng nhập nội dung"
            page.snack_bar.open = True
            page.update()
            return

        src_code = _lang_code(src_lang.value)
        dst_code = _lang_code(dst_lang.value)
        domain = domain_dd.value if use_context.value else None

        translate_btn.disabled = True
        prog.visible = True
        page.update()

        def worker():
            try:
                result = translate_text(text, src_code, dst_code, domain)
            except Exception as ex:
                result = f"[Lỗi] {ex}"

            add_history(src_code, dst_code, text, result, domain)

            output_text.value = result
            translate_btn.disabled = False
            prog.visible = False
            page.update()

        page.run_thread(worker)

    translate_btn.on_click = do_translate

    # -------------------- History --------------------
    history_btn = ft.IconButton(icon=ft.Icons.HISTORY, tooltip="Xem lịch sử")
    def show_history(e):
        items = get_history()
        if not items:
            page.snack_bar.content.value = "Chưa có lịch sử dịch"
            page.snack_bar.open = True
            page.update()
            return

        history_view = ft.ListView(expand=True)
        for src, dst, text_in, text_out, ctx, created in items:
            history_view.controls.append(
                ft.ListTile(
                    title=ft.Text(f"{src} → {dst} | {ctx or 'Không rõ ngữ cảnh'} | {created}"),
                    subtitle=ft.Text(f" {text_in}\n {text_out}"),
                    dense=True
                )
            )

        def close_dialog(e):
            page.dialog.open = False
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(" Lịch sử dịch gần đây"),
            content=ft.Container(history_view, width=600, height=400),
            actions=[ft.TextButton("Đóng", on_click=close_dialog)]
        )

        page.dialog = dlg
        page.dialog.open = True
        page.update()

    history_btn.on_click = show_history    

    # -------------------- Layout --------------------
    page.add(
        ft.Row([src_lang, swap_btn, dst_lang, file_btn, img_btn, mic_btn, history_btn], alignment="start"),
        input_text,
        ft.Row([use_context, domain_dd, translate_btn, prog], alignment="spaceBetween"),
        output_text,
        ft.Row([copy_btn, speak_btn], alignment="end"),
    )
    page.overlay.append(page.snack_bar)


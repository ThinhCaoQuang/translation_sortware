import os
import flet as ft
from api import translate_text, LANGUAGES, CONTEXTS
from text_to_speech import speak
from speech_to_text import transcribe_audio

# OCR: dùng nếu có, nếu thiếu sẽ báo snack bar khi bấm
try:
    from PIL import Image
    import pytesseract
    _HAS_OCR = True
except Exception:
    _HAS_OCR = False


def _lang_code(display: str) -> str:
    return LANGUAGES.get(display, "auto")


def main(page: ft.Page):
    page.title = "Phần mềm dịch thuật"
    page.theme_mode = "dark"
    page.padding = 20
    page.vertical_alignment = "start"
    page.scroll = "adaptive"

    # -------------------- Language controls --------------------
    src_lang = ft.Dropdown(
        label="Ngôn ngữ nguồn",
        options=[ft.dropdown.Option(lang) for lang in LANGUAGES.keys()],
        value="Auto Detect",
        width=170,
    )
    dst_lang = ft.Dropdown(
        label="Ngôn ngữ đích",
        options=[ft.dropdown.Option(lang) for lang in LANGUAGES.keys()],
        value="Tiếng Việt",
        width=170,
    )

    swap_btn = ft.IconButton(icon=ft.icons.SWAP_HORIZ, tooltip="Đổi chiều")
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
        value="General",
        width=220,
    )

    # -------------------- File pickers --------------------
    pick_txt = ft.FilePicker()
    pick_any = ft.FilePicker()
    page.overlay.append(pick_txt)
    page.overlay.append(pick_any)

    def on_pick_txt(e: ft.FilePickerResultEvent):
        if e.files:
            p = e.files[0].path
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as rf:
                    input_text.value = rf.read()
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Lỗi đọc file: {ex}"))
                page.snack_bar.open = True
                page.update()

    pick_txt.on_result = on_pick_txt

    def on_pick_any(e: ft.FilePickerResultEvent):
        if not e.files:
            return
        p = e.files[0].path.lower()
        try:
            if p.endswith((".wav", ".mp3", ".m4a", ".flac", ".ogg")):
                # STT cho file âm thanh
                txt = transcribe_audio(e.files[0].path)
                input_text.value = txt
            elif p.endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
                # OCR cho ảnh
                if not _HAS_OCR:
                    raise RuntimeError("Thiếu thư viện OCR (pillow, pytesseract).")
                img = Image.open(e.files[0].path)
                input_text.value = (pytesseract.image_to_string(img) or "").strip()
            else:
                # Thử đọc như .txt
                with open(e.files[0].path, "r", encoding="utf-8", errors="ignore") as rf:
                    input_text.value = rf.read()
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Lỗi xử lý file: {ex}"))
            page.snack_bar.open = True
            page.update()

    pick_any.on_result = on_pick_any

    file_btn = ft.IconButton(icon=ft.icons.UPLOAD_FILE, tooltip="Mở .txt",
                             on_click=lambda e: pick_txt.pick_files(allow_multiple=False, allowed_extensions=["txt"]))
    img_btn  = ft.IconButton(icon=ft.icons.IMAGE, tooltip="Mở ảnh/âm thanh/khác",
                             on_click=lambda e: pick_any.pick_files(allow_multiple=False))

    # -------------------- Copy / Speak --------------------
    copy_btn = ft.IconButton(icon=ft.icons.CONTENT_COPY, tooltip="Copy")
    def do_copy(e):
        page.set_clipboard(output_text.value or "")
        page.snack_bar = ft.SnackBar(ft.Text("Đã copy vào clipboard"))
        page.snack_bar.open = True
        page.update()
    copy_btn.on_click = do_copy

    speak_btn = ft.IconButton(icon=ft.icons.VOLUME_UP, tooltip="Đọc")
    def do_speak(e):
        try:
            speak(output_text.value or "")
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"TTS lỗi: {ex}"))
            page.snack_bar.open = True
            page.update()
    speak_btn.on_click = do_speak

    # -------------------- Translate --------------------
    prog = ft.ProgressBar(visible=False)
    translate_btn = ft.ElevatedButton(text="Dịch")

    def do_translate(e):
        text = (input_text.value or "").strip()
        if not text:
            page.snack_bar = ft.SnackBar(ft.Text("Vui lòng nhập nội dung"))
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
            output_text.value = result
            translate_btn.disabled = False
            prog.visible = False
            page.update()

        page.run_thread(worker)

    translate_btn.on_click = do_translate

    # -------------------- Layout --------------------
    page.add(
        ft.Row([src_lang, swap_btn, dst_lang, file_btn, img_btn], alignment="start"),
        input_text,
        ft.Row([use_context, domain_dd, translate_btn, prog], alignment="spaceBetween"),
        output_text,
        ft.Row([copy_btn, speak_btn], alignment="end"),
    )

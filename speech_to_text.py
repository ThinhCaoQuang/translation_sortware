import speech_recognition as sr

def transcribe_audio(lang="vi-VN") -> str:
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Đang nghe... Hãy nói đi:")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language=lang)
        print(f"Bạn đã nói: {text}")
        return text
    except sr.UnknownValueError:
        print("Không hiểu được âm thanh.")
        return ""
    except sr.RequestError as e:
        print(f"🔌 Lỗi kết nối API Google: {e}")
        return ""
    
def transcribe_audio_file(file_path: str, lang="vi-VN") -> str:
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio, language=lang)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        return f"[Lỗi kết nối API: {e}]"
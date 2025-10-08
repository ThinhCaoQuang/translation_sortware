def speak(text: str):
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text or "No content")
        engine.runAndWait()
    except Exception as ex:
        raise RuntimeError(f"TTS error: {ex}")

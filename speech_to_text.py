from openai import OpenAI
from config import settings

def transcribe_audio(file_path: str, model: str = "gpt-4o-mini-transcribe") -> str:
    """
    Trả về text đã nhận dạng từ audio. 
    Cần API key hợp lệ trong config.settings.openai_api_key.
    Gợi ý: bạn có thể đổi sang "whisper-1" nếu tài khoản hỗ trợ.
    """
    client = OpenAI(api_key=settings.openai_api_key)
    with open(file_path, "rb") as f:
        resp = client.audio.transcriptions.create(model=model, file=f)
    # SDK v1.40 trở lên: trả về resp.text
    return getattr(resp, "text", "")

import google.generativeai as genai
import sounddevice as sd
import numpy as np
import tempfile
import wave
import threading
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY", "AIzaSyDrF1Nq2RUxRJ10CPAYEt1_8bxqq45Of70"))

is_recording = False
frames = []
samplerate = 16000

def _callback(indata, frames_count, time_info, status):
    if is_recording:
        frames.append(indata.copy())

def start_recording():
    global is_recording, frames
    frames = []
    is_recording = True
    print("Bắt đầu ghi âm...")
    threading.Thread(target=_record_thread, daemon=True).start()

def _record_thread():
    with sd.InputStream(channels=1, samplerate=samplerate, dtype='int16', callback=_callback):
        while is_recording:
            sd.sleep(100)

def stop_recording():
    global is_recording
    is_recording = False
    print("Dừng ghi âm.")
    sd.sleep(200)  # đảm bảo ghi nốt phần cuối
    if not frames:
        return None
    audio = np.concatenate(frames, axis=0)
    try:
        import noisereduce as nr
        print("Đang lọc nhiễu, vui lòng đợi...")
        reduced = nr.reduce_noise(y=audio.astype(np.float32), sr=samplerate)
        print("Hoàn tất lọc nhiễu.")
        return reduced.astype(np.int16)  # chuyển lại int16 để lưu WAV
    except ImportError:
        print("Chưa cài noisereduce. Dùng âm thanh gốc.")
        return audio
    except Exception as e:
        print(f"Lỗi khi lọc nhiễu: {e}")
        return audio

def transcribe_audio(lang="vi"):
    """Dừng ghi và gửi audio đến Gemini để nhận dạng"""
    audio = stop_recording()
    if audio is None:
        return "[Không có âm thanh]"

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            with wave.open(f, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(samplerate)
                wf.writeframes(audio.tobytes())
            f.flush()

            model = genai.GenerativeModel("gemini-2.0-flash")
            prompt = (f"Chuyển nội dung giọng nói trong file này thành văn bản"
                      f"Nếu người nói dùng tiếng {lang}, hãy ghi lại nguyên văn bằng tiếng {lang}."
                      f"Không tự động đưa ra kết quả dịch khi tôi nói tiếng {lang}")

            print("Đang nhận dạng bằng Gemini...")
            response = model.generate_content([
                prompt,
                {"mime_type": "audio/wav", "data": open(f.name, "rb").read()}
            ])
            text = response.text.strip() if response.text else "[Không có kết quả]"
            print("Kết quả:", text)
            return text
    except Exception as e:
        print(f"Lỗi nhận dạng: {e}")
        return f"[Lỗi: {e}]"

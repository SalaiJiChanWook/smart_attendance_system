import os
import json
import sounddevice as sd
import queue
from vosk import Model, KaldiRecognizer
from core.local_storage import export_to_excel
from datetime import datetime

q = queue.Queue()

def callback(indata, frames, time_info, status):
    q.put(bytes(indata))

def run_voice_controller():
    # Vosk ??????? Offline Model ??? ?????????
    model_path = os.path.expanduser("~/smart_attendance_system/ai_engine/models/vosk-model-small")
    if not os.path.exists(model_path):
        print("[VOICE] Vosk model not found. Voice commands bypassed.")
        return

    model = Model(model_path)
    rec = KaldiRecognizer(model, 16000)

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):
        print("[VOICE] Voice Assistant Listening...")
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                
                # ???????? Command ?????????????? ????????????
                if "export" in text or "??????????" in text:
                    today = datetime.now().strftime("%Y-%m-%d")
                    export_to_excel(today)
                    os.system('espeak "Attendance exported successfully"')
                elif "stop" in text or "???" in text:
                    break

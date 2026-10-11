# -*- coding: utf-8 -*-
import cv2
import numpy as np
import urllib.request
import threading
import time
from ai_engine.face_recognizer import FaceRecognizer
from core.local_storage import init_db
from core.cloud_sync import start_auto_sync_thread

# ESP32-CAM ? Stream URL
STREAM_URL = "http://10.199.48.130"

def main():
    init_db()
    
    # ???????????? ??????????? Google Sheets ???? ??????????? Sync ???????? Thread
    start_auto_sync_thread(interval_sec=30)

    recognizer = FaceRecognizer()
    print(f"[STREAM] Connecting to ESP32-CAM: {STREAM_URL}")
    
    try:
        stream = urllib.request.urlopen(STREAM_URL, timeout=10)
    except Exception as e:
        print(f"[ERROR] Could not connect to camera: {e}")
        return

    bytes_data = b''
    print(">> Smart Attendance System is Running! (Headless Mode) <<")
    print(">> ????????????? Terminal ???? Ctrl + C ??? ???????? <<\n")

    last_log_time = time.time()

    try:
        while True:
            bytes_data += stream.read(4096)
            a = bytes_data.find(b'\xff\xd8')
            b = bytes_data.find(b'\xff\xd9')

            if a != -1 and b != -1:
                jpg = bytes_data[a:b+2]
                bytes_data = bytes_data[b+2:]
                
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                if frame is None:
                    continue

                processed_frame, detected_entities = recognizer.process_frame(frame)
                cv2.imshow("Raspberry Pi - Smart Attendance Console", processed_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                if detected_entities:
                    for entity in detected_entities:
                        if entity['name'] != "Unknown":
                            print(f"[DETECTED] {entity['name']} - Confidence: {int(entity['conf'] * 100)}%")

                if time.time() - last_log_time > 5:
                    print("[SYSTEM] Monitoring stream actively...")
                    last_log_time = time.time()

    except KeyboardInterrupt:
        print("\n[SYSTEM] Attendance System ??? ??????????????????")
    except Exception as e:
        print(f"\n[STREAM ERROR] {e}")
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

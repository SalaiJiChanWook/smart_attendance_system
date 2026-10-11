# -*- coding: utf-8 -*-
import cv2
import numpy as np
import urllib.request
import time
from flask import Flask, Response
from ai_engine.face_recognizer import FaceRecognizer
from core.local_storage import init_db
from core.cloud_sync import start_auto_sync_thread

app = Flask(__name__)

STREAM_URL = "http://10.199.48.130"
output_frame = None

def recognition_worker():
    global output_frame
    init_db()
    start_auto_sync_thread(interval_sec=30)
    recognizer = FaceRecognizer()

    print(f"[STREAM] Connecting to ESP32-CAM: {STREAM_URL}")
    try:
        stream = urllib.request.urlopen(STREAM_URL, timeout=10)
    except Exception as e:
        print(f"[ERROR] Could not connect to camera: {e}")
        return

    bytes_data = b''
    print(">> AI Face Recognition is running for Web Stream! <<")

    while True:
        try:
            bytes_data += stream.read(4096)
            a = bytes_data.find(b'\xff\xd8')
            b = bytes_data.find(b'\xff\xd9')

            if a != -1 and b != -1:
                jpg = bytes_data[a:b+2]
                bytes_data = bytes_data[b+2:]
                
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                if frame is None:
                    continue

                # AI Engine ????? ?????????????? Attendance ?????????
                processed_frame, entities = recognizer.process_frame(frame)

                # Browser ???? ?????????? Frame ??? Global Variable ?? ??????????
                output_frame = processed_frame.copy()

        except Exception as e:
            print(f"[ERROR] Stream interrupted: {e}")
            time.sleep(1)

def generate():
    global output_frame
    while True:
        if output_frame is None:
            time.sleep(0.05)
            continue

        # Frame ??? JPEG ????? Encode ?????????
        (flag, encoded_image) = cv2.imencode(".jpg", output_frame)
        if not flag:
            continue

        # MJPEG Stream ????? Browser ???? Feed ????????
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encoded_image) + b'\r\n')

@app.route('/')
def index():
    return '''
    <html>
        <head>
            <title>Smart Attendance Live Monitor</title>
            <style>
                body { background-color: #1a1a1a; color: white; text-align: center; font-family: Arial; }
                h2 { margin-top: 20px; }
                img { border: 3px solid #00ff00; border-radius: 8px; width: 640px; max-width: 90%; }
            </style>
        </head>
        <body>
            <h2>Live Attendance Console</h2>
            <img src="/video_feed">
        </body>
    </html>
    '''

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    import threading
    # AI Thread ??? ??????? Background Run ???????
    t = threading.Thread(target=recognition_worker, daemon=True)
    t.start()
    
    # Flask Web Server ??? Port 5000 ????? ??????????
    app.run(host='0.0.0.0', port=5000, debug=False)

import cv2
import numpy as np
import pickle
import os
import glob
from keras_facenet import FaceNet
from sklearn.preprocessing import LabelEncoder
from datetime import datetime
from mtcnn.mtcnn import MTCNN
from core.local_storage import log_attendance_locally

MODEL_DIR = os.path.expanduser("~/smart_attendance_system/ai_engine/models")
CAPTURE_DIR = os.path.expanduser("~/smart_attendance_system/data/captured_faces")

class FaceRecognizer:
    def __init__(self):
        print("[AI ENGINE] Initializing FaceNet Embedder...")
        self.embedder = FaceNet()

        # 1. SVM Model ??? ??????????? ?????? Load ?????????
        model_files = glob.glob(os.path.join(MODEL_DIR, "*svm_model*.pkl"))
        if not model_files:
            raise FileNotFoundError(f"[ERROR] SVM Model (.pkl) ??? {MODEL_DIR} ?????? ???????????")
        
        with open(model_files[0], 'rb') as f:
            self.classifier = pickle.load(f)
        print(f"[AI ENGINE] Loaded Classifier: {os.path.basename(model_files[0])}")

        # 2. NPZ ????????? ?????????????????? ?????????? Encoder ?????????????
        npz_files = glob.glob(os.path.join(MODEL_DIR, "*.npz"))
        if not npz_files:
            raise FileNotFoundError(f"[ERROR] Embeddings (.npz) ???????? {MODEL_DIR} ?????? ???????????")
            
        data = np.load(npz_files[0])
        y_labels = data['arr_1'] if 'arr_1' in data else data[data.files[1]]
        
        self.encoder = LabelEncoder()
        self.encoder.fit(y_labels)
        print(f"[AI ENGINE] Recognized Classes: {list(self.encoder.classes_)}")

        # 3. OpenCV Cascade ???? ??????????????? MTCNN ??? ?????????
        print("[AI ENGINE] Initializing MTCNN Detector...")
        self.detector = MTCNN()
        os.makedirs(CAPTURE_DIR, exist_ok=True)

    def process_frame(self, frame):
        # MTCNN ??? RGB channel format ??? ?????????????
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.detector.detect_faces(rgb_frame)

        detected_entities = []

        for res in results:
            x, y, w, h = res['box']
            x, y = abs(x), abs(y)

            # ??????? Crop ????????????
            face_img = frame[y:y+h, x:x+w]
            if face_img.size == 0:
                continue

            face_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
            face_resized = cv2.resize(face_rgb, (160, 160))
            face_array = np.expand_dims(face_resized.astype('float32'), axis=0)

            # 512D Embeddings ????? ??????????????
            embeddings = self.embedder.embeddings(face_array)
            probabilities = self.classifier.predict_proba(embeddings)[0]
            best_idx = np.argmax(probabilities)
            confidence = float(probabilities[best_idx])

            # 65% ????????? ???????? ????????????
            if confidence >= 0.65:
                name = str(self.encoder.inverse_transform([best_idx])[0])
                color = (0, 255, 0)
                
                # Snapshot ????????????
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                img_path = os.path.join(CAPTURE_DIR, f"{name}_{timestamp}.jpg")
                
                # Local Storage ?? ??????????????????
                marked = log_attendance_locally(name, confidence, img_path)
                if marked:
                    cv2.imwrite(img_path, face_img)
                    print(f"[ATTENDANCE] Marked {name} ({int(confidence * 100)}%)")
            else:
                name = "Unknown"
                color = (0, 0, 255)

            label = f"{name} ({int(confidence * 100)}%)"
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            detected_entities.append({"name": name, "box": (x, y, w, h), "conf": confidence})

        return frame, detected_entities

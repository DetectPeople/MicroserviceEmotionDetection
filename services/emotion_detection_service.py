# services/emotion_detection_service.py

import cv2
import os
from fer import FER
from config import Config

class EmotionDetectionService:
    def __init__(self):
        self.detector = FER(mtcnn=True)

    def detect_emotions_in_frame(self, frame_path):
        image = cv2.imread(frame_path)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.detector.detect_emotions(rgb_image)
        annotations = []

        for i, result in enumerate(results):
            bbox = result['box']
            emotions = result['emotions']
            emotion_label = max(emotions, key=emotions.get)
            confidence = emotions[emotion_label]
            x, y, w, h = bbox
            annotations.append({
                'person_identity': f'Person_{i}',  # Assign a unique identity per detection
                'bbox': (x, y, w, h),
                'emotion': emotion_label.capitalize(),
                'confidence': confidence
            })
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(image, f"{emotion_label.capitalize()} ({confidence*100:.2f}%)", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        annotated_frame_path = os.path.join(Config.PROCESSED_FRAMES_DIR, os.path.basename(frame_path))
        annotated_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(annotated_frame_path, annotated_image)

        return annotations, annotated_frame_path

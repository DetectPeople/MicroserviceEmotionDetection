import requests
import time
import logging
from repository.video_repository import VideoRepository
from repository.frame_repository import FrameRepository
from repository.emotion_repository import EmotionRepository
from repository.person_repository import PersonRepository
from services.emotion_detection_service import EmotionDetectionService
from services.video_generation_service import VideoGenerationService
from entities import db
from entities.emotion import Emotion
from config import Config
import os

class ProcessEmotionUseCase:
    def __init__(self):
        self.video_repository = VideoRepository()
        self.frame_repository = FrameRepository()
        self.emotion_repository = EmotionRepository()
        self.person_repository = PersonRepository()
        self.emotion_service = EmotionDetectionService()
        self.video_generation_service = VideoGenerationService()

    def execute(self, video_id):
        video = self.video_repository.get_by_id(video_id)
        if not video:
            raise ValueError('Video not found')

        # Check if frames already exist for the video
        frames = self.frame_repository.get_frames_by_video_id(video_id)
        if not frames:
            logging.info("No frames found, requesting frame processing from 5001...")
            response = requests.post("http://127.0.0.1:5001/process_video", json={"video_id": video_id})

            if response.status_code != 200:
                raise ValueError(f"Error generating frames: {response.text}")

            # Retry to get frames after the generation request
            max_retries = 10
            wait_time = 2
            for attempt in range(max_retries):
                time.sleep(wait_time)
                db.session.expire_all()
                frames = self.frame_repository.get_frames_by_video_id(video_id)
                if frames:
                    logging.info(f"Frames found on attempt {attempt + 1}")
                    break
                logging.info(f"Waiting for frames... attempt {attempt + 1}/{max_retries}")

            # If frames are still not available after retries, return None to handle this in the API
            if not frames:
                logging.info("Frames still unavailable after retries.")
                return None  # Indicate that frames are not ready yet

        # Clear any previous emotions to avoid duplication in detection
        existing_emotions = self.emotion_repository.get_emotions_by_video_id(video_id)
        if existing_emotions:
            self.emotion_repository.delete_emotions_by_video_id(video_id)

        # Process frames and annotate them
        annotated_frames = []
        total_frames = len(frames)
        for idx, frame in enumerate(frames):
            annotations, annotated_frame_path = self.emotion_service.detect_emotions_in_frame(frame.path)
            frame_data = {'frame_id': frame.id, 'annotated_path': annotated_frame_path}
            annotated_frames.append(frame_data)

            for annotation in annotations:
                bbox_str = ",".join(map(str, annotation['bbox']))
                person = self.person_repository.get_or_create(video_id, annotation['person_identity'])
                emotion = Emotion(
                    frame_id=frame.id,
                    person_id=person.id,
                    emotion_type=annotation['emotion'],
                    confidence=annotation['confidence'],
                    bbox=bbox_str,
                    video_id=video.id
                )
                self.emotion_repository.save(emotion)

            progress_percent = int(((idx + 1) / total_frames) * 100)
            logging.info(f"Processed frame {idx + 1}/{total_frames} ({progress_percent}% complete)")

        # Generate annotated video
        output_video_filename = f'video_{video.id}_emotion_annotated.mp4'
        output_video_path = os.path.join(Config.ANNOTATED_VIDEOS_DIR, output_video_filename)
        self.video_generation_service.generate_video_from_frames(annotated_frames, output_video_path)

        logging.info("Emotion detection complete, annotated video generated.")
        return output_video_path



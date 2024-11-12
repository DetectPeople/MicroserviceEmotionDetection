# MicroserviceEmotionDetection/entities/frame.py

from entities import db
from entities.video import Video  # Add this import if needed
from sqlalchemy.orm import relationship

class Frame(db.Model):
    __tablename__ = 'frames'

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    frame_number = db.Column(db.Integer, nullable=False)
    path = db.Column(db.String(255), nullable=False)

    # Relationships
    emotions = db.relationship('Emotion', back_populates='frame', lazy=True)
    video = db.relationship('Video', back_populates='frames')

    def __repr__(self):
        return f'<Frame {self.frame_number} of Video {self.video_id}>'

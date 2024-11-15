# entities/person.py

from entities import db
from sqlalchemy.orm import relationship

class Person(db.Model):
    __tablename__ = 'persons'

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    identity = db.Column(db.String(100), nullable=True)  # This column must exist

    # Relationships
    emotions = db.relationship('Emotion', back_populates='person', lazy=True)
    video = db.relationship('Video', back_populates='persons')

    def __repr__(self):
        return f'<Person {self.identity or self.id} in Video {self.video_id}>'

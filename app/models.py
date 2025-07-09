from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    playlists = relationship("Playlist", back_populates="owner")

class Playlist(Base):
    __tablename__ = "playlists"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    youtube_url = Column(String)
    total_videos = Column(Integer)
    owner_id = Column(Integer, ForeignKey("users.id"))
    youtube_id = Column(String)
    
    thumbnail = Column(String, nullable=True)

    owner = relationship("User", back_populates="playlists")
    videos = relationship("Video", back_populates="playlist")

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True)
    playlist_id = Column(Integer, ForeignKey("playlists.id"))
    title = Column(String)
    duration_seconds = Column(Integer)
    scheduled_date = Column(DateTime, nullable=True)
    status = Column(String, default="Not Started")  # Not Started, In Progress, Completed, Rewatch
    notes = Column(Text, nullable=True)
    youtube_url = Column(String)
    thumbnail = Column(String)

    playlist = relationship("Playlist", back_populates="videos")

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import database, models
from app.youtube_api import get_playlist_videos
import re
from app.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/playlists", tags=["Playlists"])

def extract_playlist_id(url: str) -> str:
    # Extract ID from full URL or just return if it's already an ID
    if "list=" in url:
        match = re.search(r"list=([a-zA-Z0-9_-]+)", url)
        return match.group(1) if match else None
    return url

class PlaylistImportRequest(BaseModel):
    youtube_url: str

@router.post("/import")
async def import_playlist(
    payload: PlaylistImportRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    playlist_id = extract_playlist_id(payload.youtube_url)
    if not playlist_id:
        raise HTTPException(status_code=400, detail="Invalid playlist URL")

    data = await get_playlist_videos(playlist_id)
    if not data or not data["videos"]:
        raise HTTPException(status_code=404, detail="No videos found")

    playlist = models.Playlist(
        title=data["playlist"]["title"],
        thumbnail=data["playlist"]["thumbnail"],
        youtube_url=payload.youtube_url,
        total_videos=len(data["videos"]),
        owner_id=current_user.id
    )
    db.add(playlist)
    db.commit()
    db.refresh(playlist)

    for video in data["videos"]:
        db.add(models.Video(
            playlist_id=playlist.id,
            title=video["title"],
            duration_seconds=video["duration_seconds"],
            thumbnail=video["thumbnail"],
            youtube_url=video["youtube_url"]
        ))
    db.commit()

    return {
        "message": "Playlist imported successfully",
        "playlist_id": playlist.id,
        "playlist_title": data["playlist"]["title"],
        "playlist_thumbnail": data["playlist"]["thumbnail"],
        "videos": data["videos"]
    }

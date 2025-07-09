from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import database, models
from datetime import datetime
from app.calendar_logic import schedule_by_hours_per_day, schedule_by_target_date
from pydantic import BaseModel
from typing import Optional
from datetime import date, timedelta
from collections import defaultdict
from app.auth import get_current_user
from app.database import get_db
from app.schemas import PlaylistCreateSchema
from typing import Literal
from app import models

router = APIRouter(prefix="/calendar", tags=["Calendar"])

class VideoStatusUpdate(BaseModel):
    status: Optional[str] = None  # "Completed", etc.
    notes: Optional[str] = None
    
class ScheduleByHoursRequest(BaseModel):
    playlist_id: int
    hours_per_day: float
    start_date: str
class VideoUpdateSchema(BaseModel):
    status: Literal['Not Started', 'In Progress', 'Completed']
    notes: Optional[str] = ""

@router.post("/schedule/by-hours")
def schedule_by_hours(
    payload: ScheduleByHoursRequest,
    db: Session = Depends(database.get_db)
):
    playlist = db.query(models.Playlist).filter(models.Playlist.id == payload.playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    videos = db.query(models.Video).filter(models.Video.playlist_id == payload.playlist_id).all()
    if not videos:
        raise HTTPException(status_code=404, detail="No videos to schedule")

    start = datetime.strptime(payload.start_date, "%Y-%m-%d")
    schedule = schedule_by_hours_per_day(videos, payload.hours_per_day, start)

    for vid_id, date in schedule:
        db.query(models.Video).filter(models.Video.id == vid_id).update({
            "scheduled_date": date
        })
    db.commit()

    return {"message": "Videos scheduled successfully (by hours/day)."}

@router.post("/schedule/by-date")
def schedule_by_target(playlist_id: int, target_date: str, start_date: str, db: Session = Depends(database.get_db)):
    playlist = db.query(models.Playlist).filter(models.Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    videos = db.query(models.Video).filter(models.Video.playlist_id == playlist_id).all()
    if not videos:
        raise HTTPException(status_code=404, detail="No videos to schedule")

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(target_date, "%Y-%m-%d")
    schedule = schedule_by_target_date(videos, end, start)

    for vid_id, date in schedule:
        db.query(models.Video).filter(models.Video.id == vid_id).update({
            "scheduled_date": date
        })
    db.commit()

    return {"message": "Videos scheduled successfully (by target date)."}


# @router.put("/video/{video_id}")
# def update_video_progress(video_id: int, update: VideoStatusUpdate, db: Session = Depends(database.get_db)):
#     video = db.query(models.Video).filter(models.Video.id == video_id).first()
#     if not video:
#         raise HTTPException(status_code=404, detail="Video not found")

#     if update.status:
#         if update.status not in ["Not Started", "In Progress", "Completed", "Rewatch"]:
#             raise HTTPException(status_code=400, detail="Invalid status")
#         video.status = update.status

#     if update.notes is not None:
#         video.notes = update.notes

#     db.commit()
#     db.refresh(video)

#     return {
#         "message": "Video progress updated successfully",
#         "video": {
#             "id": video.id,
#             "title": video.title,
#             "status": video.status,
#             "notes": video.notes
#         }
#     }


@router.get("/playlist/{playlist_id}/videos")
def get_playlist_videos(playlist_id: int, db: Session = Depends(database.get_db)):
    videos = db.query(models.Video).filter(models.Video.playlist_id == playlist_id).all()
    return [
        {
            "id": v.id,
            "title": v.title,
            "scheduled_date": v.scheduled_date,
            "status": v.status,
            "notes": v.notes,
            "thumbnail": v.thumbnail,
            "youtube_url": v.youtube_url

        } for v in videos
    ]

@router.get("/playlist/{playlist_id}/progress")
def get_progress_summary(playlist_id: int, db: Session = Depends(database.get_db)):
    videos = db.query(models.Video).filter(models.Video.playlist_id == playlist_id).all()
    total = len(videos)
    completed = sum(1 for v in videos if v.status == "Completed")

    if total == 0:
        return {"total": 0, "completed": 0, "percentage": 0}

    percent = round((completed / total) * 100, 2)
    return {
        "playlist_id": playlist_id,
        "total_videos": total,
        "completed": completed,
        "percentage": percent
    }

@router.get("/playlist/{playlist_id}/streak")
def get_watch_streak(playlist_id: int, db: Session = Depends(database.get_db)):
    videos = db.query(models.Video).filter(
        models.Video.playlist_id == playlist_id,
        models.Video.status == "Completed",
        models.Video.scheduled_date != None
    ).all()

    watched_dates = {v.scheduled_date.date() for v in videos}
    if not watched_dates:
        return {"current_streak": 0, "max_streak": 0}

    sorted_dates = sorted(watched_dates)
    max_streak = 1
    current_streak = 1
    today = date.today()

    for i in range(1, len(sorted_dates)):
        if sorted_dates[i] == sorted_dates[i - 1] + timedelta(days=1):
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1

    # Check if last watched day was yesterday or today to count current streak
    last_day = sorted_dates[-1]
    if last_day == today or last_day == today - timedelta(days=1):
        current = current_streak
    else:
        current = 0

    return {"current_streak": current, "max_streak": max_streak}


@router.get("/playlist/{playlist_id}/watch-time")
def get_watch_time(playlist_id: int, db: Session = Depends(database.get_db)):
    videos = db.query(models.Video).filter(models.Video.playlist_id == playlist_id).all()
    total = sum(v.duration_seconds for v in videos)
    completed = sum(v.duration_seconds for v in videos if v.status == "Completed")

    return {
        "total_time_sec": total,
        "completed_sec": completed,
        "remaining_sec": total - completed
    }

@router.get("/playlist/{playlist_id}/chart-data")
def get_chart_summary(playlist_id: int, db: Session = Depends(database.get_db)):
    videos = db.query(models.Video).filter(models.Video.playlist_id == playlist_id).all()
    total = len(videos)
    completed = sum(1 for v in videos if v.status == "Completed")
    return {
        "total_videos": total,
        "completed_videos": completed
    }


@router.get("/playlist/{playlist_id}/calendar-view")
def get_calendar_view(playlist_id: int, db: Session = Depends(database.get_db)):
    videos = db.query(models.Video).filter(
        models.Video.playlist_id == playlist_id,
        models.Video.scheduled_date != None
    ).order_by(models.Video.scheduled_date).all()

    if not videos:
        raise HTTPException(status_code=404, detail="No scheduled videos found")

    calendar = defaultdict(list)

    for v in videos:
        date_key = v.scheduled_date.date().isoformat()
        calendar[date_key].append({
            "id": v.id,
            "title": v.title,
            "status": v.status,
            "duration_seconds": v.duration_seconds,
            "notes": v.notes,
            "youtube_url": v.youtube_url

        })

    # Convert to a sorted list
    calendar_list = [{"date": date, "videos": vids} for date, vids in sorted(calendar.items())]
    return calendar_list

from fastapi import Body

@router.put("/video/{video_id}")
def update_video(
    video_id: int,
    payload: VideoUpdateSchema = Body(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # 🛠 Update the video in DB
    video = db.query(models.Video).join(models.Playlist).filter(models.Video.id == video_id, models.Playlist.owner_id == user.id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    video.status = payload.status
    db.commit()
    db.refresh(video)

    return {"message": "Video updated successfully"}

@router.get("/user/me/dashboard")
def user_dashboard(db: Session = Depends(database.get_db), current_user = Depends(get_current_user)):
    playlists = db.query(models.Playlist).filter(models.Playlist.owner_id == current_user.id).all()
    
    result = []

    for pl in playlists:
        videos = db.query(models.Video).filter(models.Video.playlist_id == pl.id).all()
        total = len(videos)
        completed = sum(1 for v in videos if v.status == "Completed")

        current_user = Depends(get_current_user)

        # Calendar range
        dates = [v.scheduled_date for v in videos if v.scheduled_date]
        start = min(dates).date().isoformat() if dates else None
        end = max(dates).date().isoformat() if dates else None

        percent = round((completed / total) * 100, 2) if total else 0

        result.append({
            "playlist_id": pl.id,
            "title": pl.title,
            "youtube_url": pl.youtube_url,
            "total_videos": total,
            "completed": completed,
            "thumbnail": pl.thumbnail,
            "percent_complete": percent,
            "scheduled_start": start,
            "scheduled_end": end
        })

    return result



# @router.post("/playlist")
# def create_playlist(data: PlaylistCreateSchema, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
#     new_playlist = models.Playlist(
#         title=data.title,
#         youtube_url=data.youtube_url,
#         total_videos=0,
#         owner_id=current_user.id
#     )
#     db.add(new_playlist)
#     db.commit()
#     db.refresh(new_playlist)
#     return new_playlist

#     from datetime import timedelta

#     seconds_per_day = int(hours_per_day * 3600)
#     today = date.today()

#     # Get user's playlist
#     playlist = db.query(models.Playlist).filter_by(id=playlist_id, owner_id=current_user.id).first()
#     if not playlist:
#         raise HTTPException(status_code=404, detail="Playlist not found")

#     # Filter only unfinished videos (Not Started or In Progress)
#     videos = db.query(models.Video).filter(
#         models.Video.playlist_id == playlist_id,
#         models.Video.status.in_(["Not Started", "In Progress"])
#     ).order_by(models.Video.id).all()

#     if not videos:
#         return {"message": "No unfinished videos to reschedule."}

#     # Reschedule videos one by one
#     day_offset = 0
#     used_time = 0
#     current_day = today

#     for video in videos:
#         if used_time + video.duration_seconds > seconds_per_day:
#             day_offset += 1
#             used_time = 0
#             current_day = today + timedelta(days=day_offset)

#         scheduled_datetime = datetime.combine(current_day, datetime.min.time())
#         video.scheduled_date = scheduled_datetime
#         used_time += video.duration_seconds

#     db.commit()

#     return {
#         "message": f"{len(videos)} videos rescheduled starting from {today.isoformat()}",
#         "start_date": today.isoformat(),
#         "daily_limit_minutes": int(hours_per_day * 60)
#     }

@router.get("/playlist/{playlist_id}")
def get_playlist_details(playlist_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    playlist = db.query(models.Playlist).filter(
        models.Playlist.id == playlist_id,
        models.Playlist.owner_id == current_user.id
    ).first()

    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    videos = db.query(models.Video).filter(models.Video.playlist_id == playlist_id).all()
    total = len(videos)
    completed = sum(1 for v in videos if v.status == "Completed")
    percent = round((completed / total) * 100, 2) if total else 0

    # Calendar range
    dates = [v.scheduled_date for v in videos if v.scheduled_date]
    start = min(dates).date().isoformat() if dates else None
    end = max(dates).date().isoformat() if dates else None

    return {
        "id": playlist.id,
        "title": playlist.title,
        "youtube_url": playlist.youtube_url,
        "thumbnail": playlist.thumbnail,
    }

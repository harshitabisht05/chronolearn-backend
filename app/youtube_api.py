import os
import httpx
from dotenv import load_dotenv
import isodate

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

YOUTUBE_PLAYLIST_URL = "https://www.googleapis.com/youtube/v3/playlistItems"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_PLAYLIST_METADATA_URL = "https://www.googleapis.com/youtube/v3/playlists"

# Convert ISO 8601 duration to seconds
def parse_duration(iso_duration):
    duration = isodate.parse_duration(iso_duration)
    return int(duration.total_seconds())

# NEW: Fetch playlist title + thumbnail
async def get_playlist_metadata(playlist_id: str):
    api_key = os.getenv("YOUTUBE_API_KEY")  # 🔑 Make sure this is set
    if not api_key:
        raise Exception("Missing YouTube API key")
        
    async with httpx.AsyncClient() as client:
        res = await client.get(YOUTUBE_PLAYLIST_METADATA_URL, params={
            "part": "snippet",
            "id": playlist_id,
            "key": API_KEY
        })
        data = res.json()
        if "items" not in data or not data["items"]:
            return None

        snippet = data["items"][0]["snippet"]
        return {
            "title": snippet["title"],
            "thumbnail": snippet["thumbnails"].get("high", {}).get("url", "")
        }

# MAIN FUNCTION
async def get_playlist_videos(playlist_id: str):
    video_ids = []
    video_meta = []

    playlist_info = await get_playlist_metadata(playlist_id)

    async with httpx.AsyncClient() as client:
        next_page_token = None
        while True:
            params = {
                "part": "snippet",
                "maxResults": 50,
                "playlistId": playlist_id,
                "key": API_KEY,
                "pageToken": next_page_token
            }
            res = await client.get(YOUTUBE_PLAYLIST_URL, params=params)
            data = res.json()

            for item in data.get("items", []):
                snippet = item["snippet"]
                video_id = snippet["resourceId"]["videoId"]
                title = snippet["title"]
                thumbnail = snippet["thumbnails"].get("high", {}).get("url", "")

                video_ids.append(video_id)
                video_meta.append({
                    "video_id": video_id,
                    "title": title,
                    "thumbnail": thumbnail,
                    "youtube_url": f"https://www.youtube.com/watch?v={video_id}" 
                })

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break

        videos = []
        for i in range(0, len(video_ids), 50):
            ids_chunk = video_ids[i:i+50]
            res = await client.get(YOUTUBE_VIDEOS_URL, params={
                "part": "contentDetails",
                "id": ",".join(ids_chunk),
                "key": API_KEY
            })
            durations = res.json()["items"]
            for j, item in enumerate(durations):
                duration = parse_duration(item["contentDetails"]["duration"])
                video_info = video_meta[i + j]
                videos.append({
                    "video_id": video_info["video_id"],
                    "title": video_info["title"],
                    "thumbnail": video_info["thumbnail"],
                    "duration_seconds": duration,
                    "youtube_url": f"https://www.youtube.com/watch?v={video_info['video_id']}"

                })

        return {
            "playlist": playlist_info,
            "videos": videos
        }

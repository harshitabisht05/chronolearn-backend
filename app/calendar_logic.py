from datetime import datetime, timedelta

def schedule_by_hours_per_day(videos, daily_hours: float, start_date: datetime):
    daily_limit = daily_hours * 60 * 60  # convert hours to seconds
    schedule = []
    day_cursor = start_date
    current_day_total = 0

    for video in videos:
        duration = video.duration_seconds
        if current_day_total + duration > daily_limit:
            # Move to next day
            day_cursor += timedelta(days=1)
            current_day_total = 0

        schedule.append((video.id, day_cursor))
        current_day_total += duration

    return schedule


def schedule_by_target_date(videos, end_date: datetime, start_date: datetime):
    total_duration = sum(video.duration_seconds for video in videos)
    total_days = (end_date - start_date).days + 1
    daily_limit = total_duration // total_days

    schedule = []
    day_cursor = start_date
    current_day_total = 0

    for video in videos:
        duration = video.duration_seconds
        if current_day_total + duration > daily_limit:
            day_cursor += timedelta(days=1)
            current_day_total = 0

        schedule.append((video.id, day_cursor))
        current_day_total += duration

    return schedule

from datetime import date, datetime, time, timedelta


def format_duration(seconds):
    if not seconds:
        return None
    if seconds % 3600 == 0:
        hours = seconds // 3600
        return f"{hours} hr" if hours == 1 else f"{hours} hrs"
    minutes = seconds / 60
    if minutes.is_integer():
        minutes = int(minutes)
    return f"{minutes} min"


def format_distance(distance_m):
    if not distance_m:
        return None
    km = distance_m / 1000
    if km >= 1:
        return f"{km:.2f}".rstrip("0").rstrip(".") + " km"
    return f"{int(distance_m)} m"


def format_weight(weight_kg):
    if weight_kg is None:
        return None
    return f"{weight_kg:g} kg"


def current_week_range(today=None):
    today = today or date.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start, end


def current_month_range(today=None):
    today = today or date.today()
    start = today.replace(day=1)
    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
    end = next_month - timedelta(days=1)
    return start, end


def summarize_logs(logs):
    logs = list(logs)
    return {
        "count": len(logs),
        "duration_seconds": sum(log.duration_seconds or 0 for log in logs),
        "distance_m": sum(log.distance_m or 0 for log in logs),
        "sets": sum(log.sets or 0 for log in logs),
        "reps": sum(log.reps or 0 for log in logs),
    }

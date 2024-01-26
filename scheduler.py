from datetime import datetime, timedelta, timezone
import pytz

def next_schedule_time(current_time_str):
    # Updated scheduled times
    scheduled_times = ["08:00", "12:00", "16:00"]
    
    # Convert the current time string to a datetime object (UTC)
    current_time = datetime.fromisoformat(current_time_str.replace("Z", "+00:00"))

    # Check if the current time is later than the last scheduled time
    last_scheduled_time = datetime.strptime(scheduled_times[-1], "%H:%M").replace(
        year=current_time.year, 
        month=current_time.month, 
        day=current_time.day,
        tzinfo=timezone.utc)

    if current_time >= last_scheduled_time:
        # Move to the next day if current time is at or past the last scheduled time
        next_day = current_time + timedelta(days=1)
        next_day = next_day.replace(hour=0, minute=0, second=0, microsecond=0)
        next_schedule_time = next_day.replace(
            hour=int(scheduled_times[0].split(':')[0]), 
            minute=int(scheduled_times[0].split(':')[1]),
            tzinfo=timezone.utc)
        return next_schedule_time.isoformat().replace("+00:00", "Z")

    # Find the next available slot for the current day
    for time in scheduled_times:
        schedule_time = datetime.strptime(time, "%H:%M").replace(
            year=current_time.year, 
            month=current_time.month, 
            day=current_time.day,
            tzinfo=timezone.utc)
        if current_time < schedule_time:
            return schedule_time.isoformat().replace("+00:00", "Z")

def find_latest_date(dates):
    # Convert date strings to datetime objects, handling both Z and +00:00 formats
    date_objects = []
    for date in dates:
        if date.endswith('Z'):
            date = date.replace('Z', '+00:00')
        date_objects.append(datetime.fromisoformat(date))

    # Find the latest date
    latest_date = max(date_objects)

    # Convert the latest datetime object back to string format
    return latest_date.isoformat().replace("+00:00", "Z")

def convert_to_UTC1(timestamp_utc):
    dt_utc = datetime.fromisoformat(timestamp_utc.replace("Z", "+00:00"))
    tz = pytz.timezone('Europe/Berlin')
    dt = dt_utc.astimezone(tz)
    ft_dt = dt.strftime("%d %B %Y %H:%M")
    return ft_dt
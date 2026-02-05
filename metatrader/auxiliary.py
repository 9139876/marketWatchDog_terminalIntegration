import datetime

def unix_time_to_datetime(unix_time:int) -> datetime.datetime:
    return (datetime.datetime.fromtimestamp(unix_time, datetime.UTC)).replace(tzinfo=datetime.timezone(datetime.timedelta(hours=3)))
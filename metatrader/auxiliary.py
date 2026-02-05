import datetime
import calendar

from dateutil.parser import parse


def unix_time_to_datetime(unix_time:int) -> datetime.datetime:
    return (datetime.datetime.fromtimestamp(unix_time, datetime.UTC)).replace(tzinfo=datetime.timezone(datetime.timedelta(hours=3)))

def datetime_to_unix_time(date_time:datetime.datetime) -> int:
    return calendar.timegm(date_time.timetuple())

def datetime_str_to_unix_time(date_time_str: str) -> int:
    return datetime_to_unix_time(parse(date_time_str))

    # fromtimestamp(unix_time, datetime.UTC)).replace(tzinfo=datetime.timezone(datetime.timedelta(hours=3)))
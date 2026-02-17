from datetime import datetime, UTC, timezone, timedelta
from dateutil.parser import parse


def is_utc(date_time: datetime) -> bool:
    return date_time.strftime('%Z') == 'UTC'


def unix_time_to_datetime(unix_time: int) -> datetime:
    date_time = datetime.fromtimestamp(unix_time, UTC)

    # Корректировка кривого времени в MetaTrader
    corrected_date_time = date_time.replace(tzinfo=timezone(timedelta(hours=3)))

    return corrected_date_time.astimezone(UTC)

def datetime_to_unix_time(date_time: datetime) -> int:
    if not is_utc(date_time):
        raise ValueError(f'{date_time} is not UTC')

    # Корректировка кривого времени в MetaTrader
    corrected_date_time = date_time.replace(tzinfo=timezone(timedelta(hours=-3)))

    return int(corrected_date_time.timestamp())


def datetime_str_to_unix_time(date_time_str: str) -> int:
    date_time = parse(date_time_str)

    if not is_utc(date_time):
        raise ValueError(f'{date_time_str} is not UTC')

    return datetime_to_unix_time(date_time)
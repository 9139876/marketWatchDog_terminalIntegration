from dataclasses import dataclass
from datetime import datetime

from metatrader.auxiliary import unix_time_to_datetime


@dataclass
class Quote:
    date: datetime
    open: float
    high: float
    low: float
    close: float

    @staticmethod
    def create(data: tuple) -> 'Quote':
        return Quote(
            date=unix_time_to_datetime(data[0]),
            open=float(data[1]),
            high=float(data[2]),
            low=float(data[3]),
            close=float(data[4]))

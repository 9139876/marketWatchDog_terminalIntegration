from datetime import datetime


class Quote:
    def __init__(self, data):
        self.date: int = int(data[0])
        self.open: float = float(data[1])
        self.high: float = float(data[2])
        self.low: float = float(data[3])
        self.close: float = float(data[4])

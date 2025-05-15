from dataclasses import dataclass


@dataclass
class MetaTraderOpenedPosition:
    ticket: int
    time: int
    timeMsc: int
    timeUpdate: int
    timeUpdateMsc: int
    type: int
    magic: int
    identifier: int
    reason: int
    volume: float
    priceOpen: float
    stopLoss: float
    takeProfit: float
    priceCurrent: float
    swap: float
    profit: float
    symbol: str
    comment: str
    externalId: str

    @staticmethod
    def create(opened_position: tuple) -> 'MetaTraderOpenedPosition':
        return MetaTraderOpenedPosition(ticket=opened_position.ticket, time=opened_position.time, timeMsc=opened_position.time_msc, timeUpdate=opened_position.time_update, timeUpdateMsc=opened_position.time_update_msc,
                                        type=opened_position.type, magic=opened_position.magic, identifier=opened_position.identifier, reason=opened_position.reason, volume=opened_position.volume,
                                        priceOpen=opened_position.price_open, stopLoss=opened_position.sl, takeProfit=opened_position.tp, priceCurrent=opened_position.price_current, swap=opened_position.swap, profit=opened_position.profit,
                                        symbol=opened_position.symbol, comment=opened_position.comment, externalId=opened_position.external_id)

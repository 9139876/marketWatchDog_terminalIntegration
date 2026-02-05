from dataclasses import dataclass
from datetime import datetime

from MetaTrader5 import TradeDeal

from metatrader.auxiliary import unix_time_to_datetime


@dataclass
class MetaTraderDeal:
    ticket: int
    order: int
    time: datetime
    type: int
    entry: int
    magic: int
    reason: int
    positionId: int
    volume: float
    price: float
    commission: float
    swap: float
    profit: float
    fee: float
    symbol: str
    comment: str
    externalId: str

    @staticmethod
    def create(metatrader_deal: TradeDeal) -> 'MetaTraderDeal':
        return MetaTraderDeal(
            ticket=metatrader_deal.ticket,
            order=metatrader_deal.order,
            time=unix_time_to_datetime(metatrader_deal.time),
            type=metatrader_deal.type,
            entry=metatrader_deal.entry,
            magic=metatrader_deal.magic,
            reason=metatrader_deal.reason,
            positionId=metatrader_deal.position_id,
            volume=metatrader_deal.volume,
            price=metatrader_deal.price,
            commission=metatrader_deal.commission,
            swap=metatrader_deal.swap,
            profit=metatrader_deal.profit,
            fee=metatrader_deal.fee,
            symbol=metatrader_deal.symbol,
            comment=metatrader_deal.comment,
            externalId=metatrader_deal.external_id
        )

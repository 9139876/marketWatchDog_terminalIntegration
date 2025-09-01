# pyre-strict
import enum
import logging

from config import app_config
from metatrader.terminal_integration import MetaTrader5Integration


class Mt5Manager:
    def __init__(self):
        self.__terminals__: dict[Mt5DealersEnum, MetaTrader5Integration] = {
            Mt5DealersEnum.AlfaForex: MetaTrader5Integration(app_config.ALPHA_FOREX_METATRADER_PATH, logging.getLogger('mt5_alfa_forex_logger')),
            Mt5DealersEnum.Finam: MetaTrader5Integration(app_config.FINAM_METATRADER_PATH, logging.getLogger('mt5_finam_logger')),
        }

    def get(self, dealer_str: str) -> MetaTrader5Integration:
        dealer = Mt5DealersEnum[dealer_str]
        return self.__terminals__[dealer]


class Mt5DealersEnum(enum.Enum):
    AlfaForex = 'AlfaForex',
    Finam = 'Finam',

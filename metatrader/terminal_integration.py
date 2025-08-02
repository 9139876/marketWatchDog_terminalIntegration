# pyre-strict
from collections.abc import Callable
from logging import Logger

import MetaTrader5 as mt5
from MetaTrader5 import last_error
from numpy import number

from metatrader.models.metaTraderOpenedPosition import MetaTraderOpenedPosition
from metatrader.models.metaTraderQuote import Quote
from metatrader.models.metaTraderSymbolInfo import MetaTraderSymbolInfo
from metatrader.models.orderTypeEnum import Metatrader5OrderTypeEnum
from metatrader.models.timeframe_enum import Metatrader5TimeframeEnum


class MetaTrader5Integration:
    def __init__(self, metatrader_path: str, logger: Logger):
        self.logger = logger
        self.metatrader_path = metatrader_path

        if not mt5.initialize(self.metatrader_path):
            self.logger.fatal("Ошибка установки соединения с MetaTrader5 ({path}) - {err}", path=self.metatrader_path, err=mt5.last_error())
            mt5.shutdown()
        else:
            self.logger.info("Соединение с MetaTrader5 установлено")

    def __connect_and_do_work__(self, func: Callable, is_returned_value: bool = False, attempt: int = 0):
        try:
            if not is_returned_value:
                func()
                return

            result = func()
            if result is None:
                raise Exception(mt5.last_error())

            return result
        except Exception as e:
            last_mt5_error = mt5.last_error()

            if last_mt5_error[0] == -10001:  # if terminal is closed
                mt5.shutdown()
                mt5.initialize(self.metatrader_path)

                if attempt < 1:
                    return self.__connect_and_do_work__(func, is_returned_value, attempt + 1)

            self.logger.error("Ошибка при обращении к MetaTrader - {exception}, mt5 error - {mt5_error}", exception=e, mt5_error=mt5.last_error())
            raise e

    # region Terminal Info
    def get_version(self):
        def get_version_internal():
            version = mt5.version()
            return {'mtVersion': version[0], 'build': version[1], 'releaseDate': version[2]}

        return self.__connect_and_do_work__(get_version_internal, True)

    def get_info(self):
        def get_info_internal():
            return mt5.terminal_info()

        return self.__connect_and_do_work__(get_info_internal, True)

    # endregion

    # region Account info
    def get_account_info(self):

        def get_account_info_internal():
            return mt5.account_info()._asdict()

        return self.__connect_and_do_work__(get_account_info_internal, True)

    # endregion

    # region Opened Positions
    def get_opened_positions(self) -> list[MetaTraderOpenedPosition]:
        def get_opened_positions_internal():
            opened_positions = mt5.positions_get()
            return list(map(lambda x: MetaTraderOpenedPosition.create(x), opened_positions))

        return self.__connect_and_do_work__(get_opened_positions_internal, True)

    # endregion

    # region Symbol Info
    def get_symbols(self) -> MetaTraderSymbolInfo:
        def get_symbols_internal():
            symbols = mt5.symbols_get()
            return list(map(lambda x: MetaTraderSymbolInfo(x), symbols))

        return self.__connect_and_do_work__(get_symbols_internal, True)

    def get_symbol_info(self, symbol: str) -> MetaTraderSymbolInfo:
        def get_symbol_info_internal():
            symbol_info = mt5.symbol_info(symbol)
            return MetaTraderSymbolInfo(symbol_info)

        return self.__connect_and_do_work__(get_symbol_info_internal, True)

    # endregion

    # region Quotes
    def get_last_quotes(self, symbols: list[str], timeframe_str: str, requested_count: int) -> dict[str, list[Quote]]:

        def get_last_quotes_internal():
            count = min([requested_count, 5000])
            timeframe = Metatrader5TimeframeEnum[timeframe_str]
            result: dict[str, list[Quote]] = {}

            for ticker in symbols:
                try:
                    rates = mt5.copy_rates_from_pos(ticker, timeframe.value, 0, count)
                    if rates is None or len(rates) == 0:
                        result.update({ticker: []})
                        continue

                    quotes = list(map(lambda x: Quote(x), rates))
                    result.update({ticker: quotes})
                except Exception as e:
                    self.logger.error("Ошибка при получении котировок для {ticker_name} - {exception}", ticker_name=ticker, exception=e)
                    result.update({ticker: []})

            return result

        return self.__connect_and_do_work__(get_last_quotes_internal, True)

    # endregion

    # region Position Management
    def update_stop_loss(self, identifier: int, sl_value: float) -> None:

        def update_stop_loss_internal():
            positions = list(filter(lambda x: x.identifier == identifier, self.get_opened_positions()))

            if len(positions) == 0:
                raise Exception(f'По идентификатору {identifier} не найдено открытой позиции')

            if len(positions) > 1:
                raise Exception(f'По идентификатору {identifier} найдено более одной открытой позиции')

            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": positions[0].symbol,
                "volume": positions[0].volume,
                "position": identifier,
                "sl": sl_value,
                "ENUM_ORDER_STATE": mt5.ORDER_FILLING_RETURN
            }

            result = mt5.order_send(request)

            if result is not None:
                raise Exception(mt5.last_error())

            return result

        self.__connect_and_do_work__(update_stop_loss_internal)

    def close_position(self, symbol: str) -> None:

        def close_position_internal():
            result = mt5.Close(symbol)

            if result is not None:
                raise Exception(mt5.last_error())

            return result

        self.__connect_and_do_work__(close_position_internal, True)

    def open_position(self, order_type_str: str, symbol: str, volume: float):
        def open_position_internal():
            result = None
            order_type = Metatrader5OrderTypeEnum[order_type_str].value

            if order_type == Metatrader5OrderTypeEnum.ORDER_TYPE_BUY:
                result = mt5.Buy(symbol, volume)
            elif order_type == Metatrader5OrderTypeEnum.ORDER_TYPE_SELL:
                result = mt5.Sell(symbol, volume)
            else:
                raise Exception(f'{order_type} is not supported')

            if result is not None:
                raise Exception(mt5.last_error())

            return result

        self.__connect_and_do_work__(open_position_internal, True)

    # endregion

    # region order_check

    def order_calc_profit(self, action_str: str, symbol: str, volume: float, price_open: float, price_close: float) -> number:

        def order_calc_profit_internal():
            return mt5.order_calc_profit(
                Metatrader5OrderTypeEnum[action_str].value,
                symbol,
                volume,
                price_open,
                price_close)

        return self.__connect_and_do_work__(order_calc_profit_internal, True)

    # endregion

    # def update_terminal_symbols(self, symbols: list[str], verbose: bool = True) -> None:
    #     def update_terminal_symbols_internal():
    #         for symbol in symbols:
    #             res = mt5.symbol_select(symbol, True)
    #             if verbose:
    #                 print(f'{symbol}: {'Включен' if res else 'Не удалось включить'}')
    #
    #     self.__connect_and_do_work__(update_terminal_symbols_internal)

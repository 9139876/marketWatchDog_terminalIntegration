# pyre-strict
from collections.abc import Callable
from logging import Logger
from time import strptime

import MetaTrader5 as mt5
# from MetaTrader5 import last_error
from numpy import number

from metatrader.models.metaTraderOpenedPosition import MetaTraderOpenedPosition
from metatrader.models.metaTraderQuote import Quote
from metatrader.models.orderTypeEnum import Metatrader5OrderTypeEnum
from metatrader.models.timeframe_enum import Metatrader5TimeframeEnum


class MetaTrader5Integration:
    def __init__(self, metatrader_path: str, logger: Logger):
        self.logger = logger
        self.metatrader_path = metatrader_path

        self.mt5_connect_status = False
        self.mt5_connect_last_error = ''

        self.__mt5_init_internal__()

    def __mt5_init_internal__(self) -> None:
        if not mt5.initialize(self.metatrader_path):
            self.mt5_connect_status = False
            self.mt5_connect_last_error = mt5.last_error()

            self.logger.fatal("Ошибка установки соединения с MetaTrader5 ({path}) - {err}", path=self.metatrader_path, err=self.mt5_connect_last_error)

        else:
            self.mt5_connect_status = True
            self.mt5_connect_last_error = ''

            self.logger.info(f'Соединение с [{self.metatrader_path}] установлено')

    def __connect_and_do_work__(self, func: Callable, is_returned_value: bool = False, attempt: int = 1):
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
                self.__mt5_init_internal__()

                if attempt <= 3:
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
    def get_account_info(self) -> dict:

        def get_account_info_internal():
            result = mt5.account_info()

            if result is None:
                raise Exception(mt5.last_error())

            return result._asdict()

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
    def get_symbols(self) -> list[dict]:
        def get_symbols_internal():
            symbols = mt5.symbols_get()
            return list(map(lambda x: x._asdict(), symbols))

        return self.__connect_and_do_work__(get_symbols_internal, True)

    def get_symbol_info(self, symbol: str) -> dict:
        def get_symbol_info_internal():
            symbol_info = mt5.symbol_info(symbol)

            if symbol_info is None:
                raise Exception(f'Symbol \'{symbol}\' not found.')

            return symbol_info._asdict()

        return self.__connect_and_do_work__(get_symbol_info_internal, True)

    # endregion

    # region Quotes
    def get_last_quotes(self, symbols: list[str], timeframe_str: str, requested_count: int) -> dict[str, list[Quote]]:

        def get_last_quotes_internal():
            count = min([requested_count, 5000])
            timeframe = Metatrader5TimeframeEnum[timeframe_str]
            result: dict[str, list[Quote]] = {}

            for symbol in symbols:
                try:
                    rates = mt5.copy_rates_from_pos(symbol, timeframe.value, 0, count)
                    if rates is None or len(rates) == 0:
                        result.update({symbol: []})
                        continue

                    quotes = list(map(lambda x: Quote(x), rates))
                    result.update({symbol: quotes})
                except Exception as e:
                    self.logger.error("Ошибка при получении котировок для {symbol} - {exception}", symbol=symbol, exception=e)
                    result.update({symbol: []})

            return result

        return self.__connect_and_do_work__(get_last_quotes_internal, True)

    def get_quotes(self, symbol: str, timeframe_str: str, requested_count: int) -> list[Quote]:

        def get_quotes_internal():
            if requested_count <= 0:
                return []

            timeframe = Metatrader5TimeframeEnum[timeframe_str]
            result: list[Quote] = []
            start_position = 0

            while start_position < requested_count:
                try:
                    count = min([requested_count - len(result), 5000])
                    rates = mt5.copy_rates_from_pos(symbol, timeframe.value, start_position, count)

                    if rates is None or len(rates) == 0:
                        break

                    quotes = list(map(lambda x: Quote(x), rates))
                    result.extend(quotes)
                    start_position += len(quotes)

                except Exception as e:
                    self.logger.error("Ошибка при получении котировок для {symbol} - {exception}", symbol=symbol, exception=e)
                    result = []
                    break

            return result

        return self.__connect_and_do_work__(get_quotes_internal, True)

    # Not checked!!!
    def get_range_quotes(self, symbols: list[str], timeframe_str: str, date_from_str: str, date_to_str: str) -> dict[str, list[Quote]]:
        def get_range_quotes_internal():
            timeframe = Metatrader5TimeframeEnum[timeframe_str]
            date_from = strptime(date_from_str)
            date_to = strptime(date_to_str)
            result: dict[str, list[Quote]] = {}

            for symbol in symbols:
                try:
                    rates = mt5.copy_rates_range(symbol, timeframe.value, date_from, date_to)
                    if rates is None or len(rates) == 0:
                        result.update({symbol: []})
                        continue

                    quotes = list(map(lambda x: Quote(x), rates))
                    result.update({symbol: quotes})
                except Exception as e:
                    self.logger.error("Ошибка при получении котировок для {symbol} - {exception}", symbol=symbol, exception=e)
                    result.update({symbol: []})

            return result

        return self.__connect_and_do_work__(get_range_quotes_internal, True)

    # endregion

    # region Position Management
    def update_stop_loss(self, identifier: int, sl_value: float) -> dict:

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

            if result is None:
                raise Exception(mt5.last_error())

            return result._asdict()

        return self.__connect_and_do_work__(update_stop_loss_internal)

    def open_position(self, action_str: str, symbol: str, volume: float, stop_loss: float) -> dict:
        def open_position_internal():
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": Metatrader5OrderTypeEnum[action_str].value,
                "sl": stop_loss
            }

            result = mt5.order_send(request)

            if result is None:
                raise Exception(mt5.last_error())

            return result._asdict()

        return self.__connect_and_do_work__(open_position_internal, True)

    def close_position(self, symbol: str) -> dict:

        def close_position_internal():
            result = mt5.Close(symbol)

            if result is None:
                raise Exception(mt5.last_error())

            return result._asdict()

        return self.__connect_and_do_work__(close_position_internal, True)

    # endregion

    # region order_check

    def order_calc_profit(self, action_str: str, symbol: str, volume: float, price_open: float, price_close: float) -> number:
        def order_calc_profit_internal():
            result = mt5.order_calc_profit(
                Metatrader5OrderTypeEnum[action_str].value,
                symbol,
                volume,
                price_open,
                price_close
            )

            if result is None:
                raise Exception(mt5.last_error())

            return result

        return self.__connect_and_do_work__(order_calc_profit_internal, True)

    def order_calc_margin(self, action_str: str, symbol: str, volume: float, price_open: float) -> number:
        def order_calc_margin_internal():
            result = mt5.order_calc_margin(
                Metatrader5OrderTypeEnum[action_str].value,
                symbol,
                volume,
                price_open
            )

            if result is None:
                raise Exception(mt5.last_error())

            return result

        return self.__connect_and_do_work__(order_calc_margin_internal, True)

    def order_check(self, action_str: str, symbol: str, volume: float, stop_loss: float) -> dict:
        def order_check_internal():
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": Metatrader5OrderTypeEnum[action_str].value,
                "sl": stop_loss
            }

            result = mt5.order_check(request)

            if result is None:
                raise Exception(mt5.last_error())

            return result._asdict()

        return self.__connect_and_do_work__(order_check_internal, True)

    # endregion

    # region history
    def history_deals_get(self, date_from: int) -> list[dict]:
        def history_deals_get_internal():
            result = mt5.history_deals_get(date_from, 2147483647)

            if result is None:
                raise Exception(mt5.last_error())

            return list(map(lambda x: x._asdict(), result))

        return self.__connect_and_do_work__(history_deals_get_internal, True)

    def history_orders_get(self, date_from: int) -> list[dict]:
        def history_orders_get_internal():
            result = mt5.history_orders_get(date_from, 2147483647)

            if result is None:
                raise Exception(mt5.last_error())

            return list(map(lambda x: x._asdict(), result))

        return self.__connect_and_do_work__(history_orders_get_internal, True)
    # endregion

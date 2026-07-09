import logging
import jsonpickle
import requests

from metatrader.auxiliary import datetime_str_to_utc_str
from metatrader.terminal_integration import MetaTrader5Integration


class Monitoring:

    def __init__(self, server_url: str, secret_key: str, component_id: str, unit_test_id: str):
        self.serverUrl = server_url
        self.secretKey = secret_key
        self.component_id = component_id
        self.unit_test_id = unit_test_id

    @staticmethod
    def __convert_log_level__(level_name: str):
        match level_name:
            case 'DEBUG':
                return 'Debug'
            case 'INFO':
                return 'Info'
            case 'WARNING':
                return 'Warning'
            case 'ERROR':
                return 'Error'
            case 'CRITICAL':
                return 'Fatal'
            case _:
                return 'Info'

    def logger_callback(self, record: logging.LogRecord):
        request = {
            "Token": {"SecretKey": self.secretKey},
            "Data": {"ComponentId": self.component_id,
                     "Date": datetime_str_to_utc_str(record.asctime),
                     "Level": self.__convert_log_level__(record.levelname),
                     "Message": record.msg}
        }

        url = f"{self.serverUrl}/SendLog"
        json = jsonpickle.encode(request)

        try:
            requests.post(url, data=json)
        except Exception:
            pass

    def send_i_am_alive(self, mt5: MetaTrader5Integration):
        terminal_info = mt5.get_info()

        if terminal_info is not None and terminal_info.connected:
            request = {
                "Token": {"SecretKey": self.secretKey},
                "Data": {"UnitTestId": self.unit_test_id,
                         "Result": "Success",
                         "Message": "Приложение работает нормально",
                         "ActualIntervalSeconds": 45}
            }

            url = f"{self.serverUrl}/SendUnitTestResult"
            json = jsonpickle.encode(request)

            try:
                requests.post(url, data=json)
            except Exception:
                pass

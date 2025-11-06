import json
from collections.abc import Callable

from metatrader.terminal_integration import MetaTrader5Integration


def __serialize_success_response__(payload: str) -> str:
    return '{"isSuccess": true, "payload": ' + payload + '}'


def __serialize_error_response__(ex: Exception | str | tuple) -> str:
    if isinstance(ex, tuple) and len(ex) >= 2:
        error_message = f'Error - {ex[1]} (code:{ex[0]})'
        response = {"isSuccess": False, "errorMessage": f'{error_message}'}
    else:
        response = {"isSuccess": False, "errorMessage": f'{ex}'}

    return json.dumps(response)


def execute(func: Callable, mt5: MetaTrader5Integration) -> str:
    if not mt5.mt5_connect_status:
        return __serialize_error_response__(mt5.mt5_connect_last_error)

    try:
        payload = func()
        return __serialize_success_response__(payload)
    except Exception as e:
        return __serialize_error_response__(e)


def snake_to_camel_case(snake_str: str) -> str:
    return "".join(x.capitalize() for x in snake_str.lower().split("_"))


def snake_to_lower_camel_case(snake_str: str) -> str:
    # We capitalize the first letter of each component except the first one
    # with the 'capitalize' method and join them together.
    camel_string = snake_to_camel_case(snake_str)
    return snake_str[0].lower() + camel_string[1:]


def dict_keys_modify(dictionary: dict, modifier: Callable) -> dict:
    new_dictionary = {}

    for key, value in dictionary.items():
        new_dictionary[modifier(key)] = value

    return new_dictionary

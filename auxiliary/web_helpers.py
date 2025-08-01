import json
from collections.abc import Callable


def __serialize_success_response__(payload: str) -> str:
    return '{"isSuccess": true, "payload": ' + payload + '}'


def __serialize_error_response__(ex: Exception) -> str:
    response = {"isSuccess": False, "errorMessage": f'{type(ex)} - {ex}'}
    return json.dumps(response)


def execute(func: Callable) -> str:
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


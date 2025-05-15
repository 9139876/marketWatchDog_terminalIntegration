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

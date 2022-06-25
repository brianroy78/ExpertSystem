import json
from typing import Any, Tuple, Dict


def normalize(data) -> Tuple[str, int, Dict[str, str]]:
    return json.dumps(data, default=str), 200, {'Content-Type': 'application/json'}


def as_json(data: Any) -> Tuple[str, int, Dict[str, str]]:
    return normalize({'status': 'OK', 'data': data})


def return_error(msg: str) -> Tuple[str, int, Dict[str, str]]:
    return normalize({'error': msg})


def return_ok() -> Tuple[str, int, Dict[str, str]]:
    return normalize({'status': 'OK'})

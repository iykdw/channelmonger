from typing import Any
from typing import List

from inquirer import errors

def tx_mhz_frequency_validator(value):
    value = float(value)
    if not 134.0 <= value <= 174.0 and not 400.0 <= value <= 480.0:
        return False

    return value

def inquirer_mhz_frequency_validator(_, value):
    value = float(value)
    if not 134.0 <= value <= 174.8 and not 400.0 <= value <= 480.0:
        raise errors.ValidationError('', reason='Frequeny is outwith firmware limits!')

    return True

def is_integer(value):
    try:
        return int(value)
    except:
        return False

def is_float(value):
    try:
        return float(value)
    except:
        return False

def import_zone_members(string: str) -> List[Any]:
    return string.split("|")

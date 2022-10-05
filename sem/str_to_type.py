"""
Common type conversion from string.
Mainly to be using during argument parsing from strings.
"""

from collections.abc import Callable
from typing import Any, Optional, Union


def bool_type(x: str) -> bool:
    """Convert a valid string to a boolean.
    Valid strings are: "0", "1", "true" and "false".
    The conversion is case-insensitive.
    """
    x = x.strip()
    if x == "1" or x.lower() == "true":
        return True
    if x == "0" or x.lower() == "false":
        return False

    raise ValueError("The input cannot be converted to a boolean")


def none_or_type(default_type: Callable) -> Callable:
    """Return a new type function.
    The new functions parses the "None" string (in a case insensitive fashion),
    otherwise calls a predefined function default_type.
    """

    def new_type_fn(x: str) -> Optional[Any]:
        x = x.strip()
        if x.lower() == "none":
            return None
        return default_type(x)

    return new_type_fn


def unit_float_or_positive_integer(x: str, valid_zero=True) -> Union[int, float]:
    """Convert a string to a float within the open interval (0, 1) or to a positive
    integer.
    Zero is considered a valid integer input depending on the value of valid_zero.
    This type of input is utilized in many libraries where it either represents a
    fraction (i.e. a value between 0 and 1), or a an absolute count of objects.
    """
    x = float(x)

    if x < 0:
        raise ValueError("Invalid input ", x, " : less or equal than 0.")
    if x == 0 and not valid_zero:
        raise ValueError(
            "Invalid zero input. If you wish to accept zero as input, set valid_zero to True."
        )
    if x > 1 and not x.is_integer():
        raise ValueError("Can only accept float values in the range (0, 1).")

    if x.is_integer():
        return int(x)
    return x

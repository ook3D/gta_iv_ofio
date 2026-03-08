from typing import TextIO, Union


def to_bool(element: str) -> bool:
    if element.lower() in ["true", "1"]:
        return True
    elif element.lower() in ["false", "0"]:
        return False
    else:
        raise ValueError


def is_float(element: any) -> bool:
    """Check if the element can be converted to a float."""
    try:
        float(element)
        return True
    except (ValueError, TypeError):
        return False


def convert_str(
    element: list[str] | tuple[str] | str,
) -> list[None | int | float | str] | float | int | None | str:
    """Convert string or list/tuple of strings to appropriate data types."""

    def convert_value(value: str):
        """Helper function to convert individual string to the appropriate type."""
        if value in ["none", "null", "nil", "*NULL*"]:
            return None
        elif value.isnumeric():
            return int(value)
        elif is_float(value):
            return float(value)
        else:
            return value

    if isinstance(element, (list, tuple)):
        return [convert_value(part) for part in element if isinstance(part, str)]

    return convert_value(element)


def to_int(string: Union[list, tuple]) -> list[int]:
    return [int(x) for x in string]


def to_float(string: Union[str, list, tuple]) -> float | list[float]:
    return [float(x) for x in string]


def to_none(string: Union[str, list, tuple]) -> list[int | None] | None | int:
    def _to_none(element: str) -> None | int:
        if element in ["none", "null", "nil", "*NULL*"]:
            return None
        else:  # hardcoding for `lodgroup` section in drawable
            return int(element)

    if isinstance(string, Union[list, tuple]):
        return [_to_none(x) for x in string]
    return _to_none(string)


def jump_to(symbol: str, file: TextIO) -> str:
    """
    Jump to the line containing the specified symbol in the file.

    Args:
        symbol (str): The symbol to search for.
        file (TextIO): The file object to read from.

    Returns:
        str: The line containing the symbol or an empty string if not found.
    """
    line = file.readline()
    while symbol not in line and line != "":
        line = file.readline()
    return line

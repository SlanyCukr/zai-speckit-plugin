#!/usr/bin/env python3
"""TOON (Token-Optimized Object Notation) parser.

TOON is a compact serialization format that reduces tokens compared to JSON:
- Simple key-value pairs
- YAML-like indentation for nested dicts
- Inline CSV for primitive arrays
- Tabular format for object arrays

This is a READ-ONLY parser for TOON format. It converts TOON text to Python
dicts/lists. Agents should write TOON format directly as text rather than using
a Python library for serialization.
"""

from __future__ import annotations

from typing import Any


def loads(text: str) -> dict | list:
    """Parse TOON formatted string to Python objects.

    Args:
        text: TOON formatted string

    Returns:
        Python dict or list

    Examples:
        >>> loads('key: value')
        {'key': 'value'}
        >>> loads('items[3]: 1,2,3')
        {'items': [1, 2, 3]}
    """
    if not text.strip():
        return {}

    lines = text.strip().split("\n")
    result, _ = _parse_dict(lines, 0, 0)

    # If the result is a dict with single key "items" and we started with a list,
    # return just the list
    if isinstance(result, dict) and len(result) == 1 and "items" in result:
        # Check if this was originally a top-level list
        first_line = lines[0].strip()
        if first_line.startswith("items["):
            return result["items"]

    return result


def _parse_dict(
    lines: list[str], start_idx: int, base_indent: int
) -> tuple[dict, int]:
    """Parse a dictionary from TOON lines.

    Args:
        lines: All lines from TOON text
        start_idx: Index to start parsing from
        base_indent: Indentation level for this dict (0 for root)

    Returns:
        Tuple of (parsed dict, next line index to parse)
    """
    result: dict = {}
    i = start_idx
    n = len(lines)

    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        # Calculate current indentation
        indent = len(line) - len(line.lstrip())
        current_level = indent // 2

        # If we're back to a lower indentation level, we're done with this dict
        if current_level < base_indent:
            break

        # Remove indentation
        content = line.strip()

        # Parse key and value
        if ":" not in content:
            i += 1
            continue

        key_part, value_part = content.split(":", 1)
        key = key_part.strip()
        value_part = value_part.strip()

        # Check for array notation
        if "[" in key and "]" in key:
            # Parse array
            array_size, key, schema = _parse_array_key(key)
            parsed_array, new_i = _parse_array(
                lines, i, value_part, array_size, schema, current_level + 1
            )
            result[key] = parsed_array
            i = new_i
        elif value_part == "":
            # Nested dict or empty value
            next_i = i + 1
            if next_i < n:
                next_line = lines[next_i]
                next_indent = (len(next_line) - len(next_line.lstrip())) // 2
                if next_indent > current_level:
                    # This is a nested dict
                    nested_dict, next_i = _parse_dict(lines, next_i, current_level + 1)
                    result[key] = nested_dict
                    i = next_i
                    continue
            # Empty value
            result[key] = ""
            i += 1
        else:
            # Simple key-value pair
            result[key] = _parse_value(value_part)
            i += 1

    return result, i


def _parse_array_key(key: str) -> tuple[int, str, list[str] | None]:
    """Parse array key with size and optional schema.

    Args:
        key: Key string like "items[3]" or "items[3]{name,age}"

    Returns:
        Tuple of (size, key_name, schema_list_or_None)
    """
    # Extract base key
    base_key = key.split("[")[0]

    # Extract size
    size_start = key.find("[") + 1
    size_end = key.find("]")
    size = int(key[size_start:size_end])

    # Check for schema
    schema: list[str] | None = None
    if "{" in key and "}" in key:
        schema_start = key.find("{") + 1
        schema_end = key.find("}")
        schema_str = key[schema_start:schema_end]
        schema = [s.strip() for s in schema_str.split(",") if s.strip()]

    return size, base_key, schema


def _parse_array(
    lines: list[str],
    start_idx: int,
    value_part: str,
    array_size: int,
    schema: list[str] | None,
    expected_indent: int,
) -> tuple[list, int]:
    """Parse an array from TOON lines.

    Args:
        lines: All lines from TOON text
        start_idx: Index of array declaration line
        value_part: Value part after colon (for inline arrays)
        array_size: Expected size of array
        schema: Schema keys for tabular arrays, or None for primitive arrays
        expected_indent: Expected indentation for array items

    Returns:
        Tuple of (parsed list, next line index to parse)
    """
    if array_size == 0:
        return [], start_idx + 1

    # Check if this is an inline array
    if value_part:
        # Parse inline CSV values
        values = _parse_csv_values(value_part)
        return values, start_idx + 1

    # Tabular array - parse following lines
    result: list = []
    i = start_idx + 1

    while i < len(lines) and len(result) < array_size:
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        indent = len(line) - len(line.lstrip())
        current_level = indent // 2

        # Check if we've moved out of this array
        if current_level < expected_indent:
            break

        content = line.strip()
        if schema:
            # Parse as dict using schema
            values = _parse_csv_values(content)
            row_dict: dict = {}
            for j, key in enumerate(schema):
                if j < len(values):
                    row_dict[key] = values[j]
                else:
                    row_dict[key] = ""
            result.append(row_dict)
        else:
            # Parse as primitive list
            values = _parse_csv_values(content)
            result.extend(values)

        i += 1

    return result, i


def _parse_csv_values(text: str) -> list:
    """Parse CSV values from a string, handling quoted values.

    Args:
        text: CSV string like '1,2,3' or '"a,b",c'

    Returns:
        List of parsed values
    """
    values: list = []
    current = ""
    in_quotes = False

    for char in text:
        if char == '"':
            in_quotes = not in_quotes
        elif char == "," and not in_quotes:
            values.append(_parse_value(current.strip()))
            current = ""
        else:
            current += char

    # Add last value
    if current or not values:
        values.append(_parse_value(current.strip()))

    return values


def _parse_value(value: str) -> Any:
    """Parse a single value, inferring type.

    Args:
        value: String value to parse

    Returns:
        Parsed value (str, int, float, bool, or empty string)
    """
    if not value:
        return ""

    # Remove quotes if present
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]

    # Try boolean
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False

    # Try int
    try:
        return int(value)
    except ValueError:
        pass

    # Try float
    try:
        return float(value)
    except ValueError:
        pass

    # Default to string
    return value

"""Commonly occurring patterns for regular expression parsing."""
FLOAT_PATTERN = r"[-+]?(?:\d*\.\d+|\d+)"
INT_PATTERN = r"\d+"
BOOL_PATTERN = r"True|False"
BOOL_WITH_NUMERIC_PATTERN = r"True|False|0|1"
LITERAL_PATTERN = r"[a-zA-Z]+"
# Numerical format, including exponential format.
NUMERIC_PATTERN = r"[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?"

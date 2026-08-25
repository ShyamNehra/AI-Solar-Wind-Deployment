"""
Financial Analysis Utilities and Input Validation
"""


def validate_positive_value(value: float, param_name: str) -> float:
    """
    Validates that a input numeric value is non-negative.
    """
    if value is None:
        raise ValueError(f"{param_name} cannot be None")
    val = float(value)
    if val < 0:
        raise ValueError(f"{param_name} cannot be negative")
    return val


def validate_strict_positive(value: float, param_name: str) -> float:
    """
    Validates that a numeric input value is strictly positive (> 0).
    """
    if value is None:
        raise ValueError(f"{param_name} cannot be None")
    val = float(value)
    if val <= 0:
        raise ValueError(f"{param_name} must be greater than zero")
    return val

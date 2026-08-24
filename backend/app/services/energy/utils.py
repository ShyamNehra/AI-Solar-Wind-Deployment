"""
Validation and Calculation Utility Functions for Energy Yield Estimation
"""

from typing import Tuple


def normalize_percentage(value: float, name: str = "Parameter") -> float:
    """
    Converts percentage (0-100) or decimal (0-1.0) to decimal fraction (0-1.0).
    Validates range.
    """
    if value is None:
        raise ValueError(f"{name} cannot be None")
    
    val = float(value)
    if val < 0:
        raise ValueError(f"{name} cannot be negative")
    
    if val > 100.0:
        raise ValueError(f"{name} cannot exceed 100%")
    
    if val > 1.0:
        return val / 100.0
    return val


def validate_capacity(installed_capacity: float) -> float:
    """
    Validates installed capacity in kW.
    """
    if installed_capacity is None:
        raise ValueError("Installed capacity cannot be None")
    cap = float(installed_capacity)
    if cap < 0:
        raise ValueError("Installed capacity cannot be negative")
    return cap


def validate_resource_value(value: float, resource_name: str) -> float:
    """
    Validates resource input like solar irradiance or wind speed.
    """
    if value is None:
        raise ValueError(f"{resource_name} cannot be None")
    val = float(value)
    if val < 0:
        raise ValueError(f"{resource_name} cannot be negative")
    return val

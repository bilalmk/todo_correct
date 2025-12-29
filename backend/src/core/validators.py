"""Validation helpers for application data."""
from typing import Optional
from dateutil.rrule import rrulestr


def validate_rrule(rrule_string: Optional[str]) -> bool:
    """
    Validate an iCalendar RRULE string using python-dateutil.

    Args:
        rrule_string: RRULE string to validate (e.g., "FREQ=DAILY;INTERVAL=1")

    Returns:
        bool: True if valid RRULE, False otherwise

    Examples:
        >>> validate_rrule("FREQ=DAILY")
        True
        >>> validate_rrule("FREQ=WEEKLY;BYDAY=MO,WE,FR")
        True
        >>> validate_rrule("INVALID")
        False
        >>> validate_rrule(None)
        False
    """
    if not rrule_string:
        return False

    try:
        # Attempt to parse the RRULE string
        # rrulestr expects full RFC 5545 format, so we prefix with RRULE:
        rrulestr(f"RRULE:{rrule_string}")
        return True
    except (ValueError, TypeError):
        return False


def validate_recurrence_config(config: dict) -> tuple[bool, Optional[str]]:
    """
    Validate a recurrence configuration dictionary.

    Args:
        config: Dictionary containing recurrence configuration

    Returns:
        tuple: (is_valid: bool, error_message: Optional[str])

    Expected config structure:
        {
            "rrule": "FREQ=DAILY;INTERVAL=1",  # Required
            "timezone": "UTC",  # Optional
            "end_date": "2025-12-31T23:59:59Z",  # Optional
            "exceptions": ["2025-01-01T00:00:00Z"],  # Optional
        }
    """
    if not isinstance(config, dict):
        return False, "Recurrence config must be a dictionary"

    # RRULE is required
    if "rrule" not in config:
        return False, "Missing required field: rrule"

    # Validate RRULE format
    if not validate_rrule(config["rrule"]):
        return False, f"Invalid RRULE format: {config['rrule']}"

    # Optional: validate timezone if provided
    if "timezone" in config:
        if not isinstance(config["timezone"], str):
            return False, "Timezone must be a string"

    # Optional: validate exceptions if provided
    if "exceptions" in config:
        if not isinstance(config["exceptions"], list):
            return False, "Exceptions must be a list"

    return True, None

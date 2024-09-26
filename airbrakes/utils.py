"""File which contains a few basic utility functions which can be reused in the project."""


def convert_to_nanoseconds(value) -> int:
    """Converts seconds to nanoseconds, if `value` is in float."""
    try:
        return int(float(value) * 10e9)
    except (ValueError, TypeError):
        return None


def convert_to_float(value) -> float | None:
    """Converts a value to a float, returning None if the conversion fails."""
    try:
        return float(value)  # Attempt to convert to float
    except (ValueError, TypeError):
        return None  # Return None if the conversion fails


def deadband(input_value, threshold) -> float:
    """
    Returns 0 if the input_value is within the deadband threshold.
    Otherwise, returns the input_value adjusted by the threshold.
    :param input_value: The value to apply the deadband to.
    :param threshold: The deadband threshold.
    :return: Adjusted input_value or 0 if within the deadband.
    """
    if abs(input_value) < threshold:
        return 0.0
    return input_value


def get_imu_data_processor_public_properties() -> list:
    """Returns the public properties of the IMUDataProcessor class."""
    # We have to manually list the properties because of cyclic imports :(

    return [
        "avg_acceleration",
        "avg_acceleration_mag",
        "max_altitude",
        "current_altitude",
        "speed",
        "max_speed",
    ]

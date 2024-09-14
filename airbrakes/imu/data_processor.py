"""Module for processing IMU data on a higher level."""

import statistics as stats
from collections.abc import Sequence

from airbrakes.imu.imu_data_packet import EstimatedDataPacket


class ProcessedIMUData:
    """Performs high level calculations on the data packets received from the IMU. Includes
    calculation the rolling averages of acceleration, maximum altitude so far, etc, from the set of
    data points.

    Args:
        data_points (Sequence[EstimatedDataPacket]): A list of EstimatedDataPacket objects
            to process.
    """

    __slots__ = ("_avg_accel", "_avg_accel_mag", "_max_altitude", "data_points")

    def __init__(self, data_points: Sequence[EstimatedDataPacket]):
        self.data_points: Sequence[EstimatedDataPacket] = data_points
        self._avg_accel: tuple[float, float, float] = (0.0, 0.0, 0.0)
        self._avg_accel_mag: float = 0.0
        self._max_altitude: float = 0.0

    def update_data(self, data_points: Sequence[EstimatedDataPacket]) -> None:
        """Updates the data points to process. This will recalculate the averages and maximum
        altitude."""
        self.data_points = data_points
        a_x, a_y, a_z = self.compute_averages()
        self._avg_accel = (a_x, a_y, a_z)
        self._avg_accel_mag = (self._avg_accel**2 + self._avg_accel**2 + self._avg_accel**2) ** 0.5
        self._max_altitude = max(*(data_point.altitude for data_point in self.data_points), self._max_altitude)

    def compute_averages(self) -> tuple[float, float, float]:
        """Calculates the average acceleration and acceleration magnitude of the data points."""
        # calculate the average acceleration in the x, y, and z directions
        # TODO: Test what these accel values actually look like
        x_accel = stats.fmean(data_point.estCompensatedAccelX for data_point in self.data_points)
        y_accel = stats.fmean(data_point.estCompensatedAccelY for data_point in self.data_points)
        z_accel = stats.fmean(data_point.estCompensatedAccelZ for data_point in self.data_points)
        # TODO: Calculate avg velocity if that's also available
        return x_accel, y_accel, z_accel

    @property
    def avg_acceleration_z(self) -> float:
        """Returns the average acceleration in the z direction of the data points, in m/s^2."""
        return self._avg_accel[-1]

    @property
    def avg_acceleration(self) -> tuple[float, float, float]:
        """Returns the averaged acceleration as a vector of the data points, in m/s^2."""
        return self._avg_accel

    @property
    def avg_acceleration_mag(self) -> float:
        """Returns the magnitude of the acceleration vector of the data points, in m/s^2."""
        return self._avg_accel_mag

    @property
    def max_altitude(self) -> float:
        """Returns the highest altitude attained by the rocket for the entire flight so far,
        in meters.
        """
        return self._max_altitude

    def __str__(self) -> str:
        """Returns a string representation of the ProcessedIMUData object."""
        return (
            f"{self.__class__.__name__}("
            f"avg_acceleration={self.avg_acceleration}, "
            f"avg_acceleration_mag={self.avg_acceleration_mag}, "
            f"max_altitude={self.max_altitude})"
        )

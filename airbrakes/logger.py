"""Module for logging data to a CSV file in real time."""

import collections
import csv
import multiprocessing
from pathlib import Path

from airbrakes.constants import CSV_HEADERS
from airbrakes.imu.imu_data_packet import IMUDataPacket


class Logger:
    """
    A class that logs data to a CSV file. Similar to the IMU class, it runs in a separate process. This is because the
    logging process is I/O-bound, meaning that it spends most of its time waiting for the file to be written to. By
    running it in a separate process, we can continue to log data while the main loop is running.

    It uses the Python logging module to append the airbrake's current state, extension, and IMU data to our logs in
    real time.

    Args:
        log_dir (:class:`pathlib.Path`): The directory where the log files will be.
    """

    __slots__ = ("_log_process", "_log_queue", "_running", "_stop_signal", "log_path")

    def __init__(self, log_dir: Path):
        log_dir.mkdir(parents=True, exist_ok=True)

        # Get all existing log files and find the highest suffix number
        existing_logs = list(log_dir.glob("log_*.csv"))
        max_suffix = max(int(log.stem.split("_")[-1]) for log in existing_logs) if existing_logs else 0

        # Create a new log file with the next number in sequence
        self.log_path = log_dir / f"log_{max_suffix + 1}.csv"
        with self.log_path.open(mode="w", newline="") as file_writer:
            writer = csv.DictWriter(file_writer, fieldnames=CSV_HEADERS)
            writer.writeheader()

        # Makes a queue to store log messages, basically it's a process-safe list that you add to
        # the back and pop from front, meaning that things will be logged in the order they were
        # added
        self._log_queue: multiprocessing.Queue[IMUDataPacket] = multiprocessing.Queue()
        self._running = multiprocessing.Value("b", False)  # Makes a boolean value that is shared between processes

        # Start the logging process
        self._log_process = multiprocessing.Process(target=self._logging_loop)

        # The signal to stop the logging process, this will be put in the queue to stop the process
        # see stop() and _logging_loop() for more details.
        self._stop_signal = "STOP"

    def start(self):
        """
        Starts the logging process. This is called before the main while loop starts.
        """
        self._running.value = True
        self._log_process.start()

    @property
    def is_running(self) -> bool:
        """
        Returns whether the logging process is running.
        """
        return self._running.value

    def _logging_loop(self):
        """
        The loop that saves data to the logs. It runs in parallel with the main loop.
        """
        # Set up the csv logging in the new process
        with self.log_path.open(mode="a", newline="") as file_writer:
            writer = csv.DictWriter(file_writer, fieldnames=CSV_HEADERS)
            while self._running.value:
                # Get a message from the queue (this will block until a message is available)
                # Because there's no timeout, it will wait indefinitely until it gets a message.
                message_fields = self._log_queue.get()
                if message_fields == self._stop_signal:
                    break
                writer.writerow(message_fields)

    def log(self, state: str, extension: float, imu_data_list: collections.deque[IMUDataPacket]):
        """
        Logs the current state, extension, and IMU data to the CSV file.
        :param state: the current state of the airbrakes state machine
        :param extension: the current extension of the airbrakes
        :param imu_data_list: the current list of IMU data packets to log
        """
        # Loop through all the IMU data packets
        for imu_data in imu_data_list:
            # Formats the log message as a CSV line
            message_dict = {"state": state, "extension": extension, "timestamp": imu_data.timestamp}
            message_dict.update({key: getattr(imu_data, key) for key in imu_data.__slots__})
            # Put the message in the queue
            self._log_queue.put(message_dict)

    def stop(self):
        """
        Stops the logging process. It will finish logging the current message and then stop.
        """
        self._running.value = False
        # Waits for the process to finish before stopping it
        self._log_queue.put(self._stop_signal)  # Put the stop signal in the queue
        self._log_process.join()

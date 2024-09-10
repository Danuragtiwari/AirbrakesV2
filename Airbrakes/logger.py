"""Module for logging data to a CSV file in real time."""

import logging
import multiprocessing
from pathlib import Path

from Airbrakes.imu import IMUDataPacket


class Logger:
    """
    A class that logs data to a CSV file. Similar to the IMU class, it runs in a separate process. This is because the
    logging process is I/O-bound, meaning that it spends most of its time waiting for the file to be written to. By
    running it in a separate process, we can continue to log data while the main loop is running.

    It uses the Python logging module to append the airbrake's current state, extension, and IMU data to our logs in
    real time.
    """

    __slots__ = ("csv_headers", "log_path", "log_process", "log_queue", "running")

    def __init__(self, csv_headers: list[str]):
        self.csv_headers = csv_headers

        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        # Get all existing log files and find the highest suffix number
        existing_logs = list(log_dir.glob("log_*.csv"))
        max_suffix = max(int(log.stem.split("_")[-1]) for log in existing_logs) if existing_logs else 0

        # Create a new log file with the next number in sequence
        self.log_path = log_dir / f"log_{max_suffix + 1}.csv"
        with self.log_path.open(mode="w", newline="") as file_writer:
            file_writer.write(",".join(csv_headers) + "\n")

        # Makes a queue to store log messages, basically it's a process-safe list that you add to the back and pop from
        # front, meaning that things will be logged in the order they were added
        self.log_queue = multiprocessing.Queue()
        self.running = multiprocessing.Value("b", True)  # Makes a boolean value that is shared between processes

        # Start the logging process
        self.log_process = multiprocessing.Process(target=self._logging_loop)
        self.log_process.start()

    def _logging_loop(self):
        """
        The loop that saves data to the logs. It runs in parallel with the main loop.
        """
        # Set up the logger in the new process
        logger = logging.getLogger("logger")
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(self.log_path, mode="a")  # Append to the file
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

        while self.running.value:
            # Get a message from the queue (this will block until a message is available)
            # Because there's no timeout, it will wait indefinitely until it gets a message -- this is fine in practice,
            # as >100 messages a second should be added to the queue, but if for some reason the queue is empty, it will
            # block forever and stop() won't work
            message = self.log_queue.get()
            logger.info(message)

    def log(self, state: str, extension: float, imu_data: IMUDataPacket):
        """
        Logs the current state, extension, and IMU data to the CSV file.
        :param state: the current state of the airbrakes state machine
        :param extension: the current extension of the airbrakes
        :param imu_data: the current IMU data
        """
        # Formats the log message as a CSV line
        message = f"{state},{extension},{','.join(str(getattr(imu_data, value)) for value in imu_data.__slots__)}"
        # Put the message in the queue
        self.log_queue.put(message)

    def stop(self):
        """
        Stops the logging process. It will finish logging the current message and then stop.
        """
        self.running.value = False
        # Waits for the process to finish before stopping it
        self.log_process.join()

"""The main file which will be run on the Raspberry Pi. It will create the AirbrakesContext object and run the main
loop."""

from airbrakes.airbrakes import AirbrakesContext
from airbrakes.constants import FREQUENCY, MAX_EXTENSION, MIN_EXTENSION, PORT, SERVO_PIN, UPSIDE_DOWN
from airbrakes.imu.imu import IMU
from airbrakes.logger import Logger
from airbrakes.servo import Servo


def main():
    logger = Logger()
    servo = Servo(SERVO_PIN, MIN_EXTENSION, MAX_EXTENSION)
    imu = IMU(PORT, FREQUENCY, UPSIDE_DOWN)

    # The context that will manage the airbrakes state machine
    airbrakes = AirbrakesContext(logger, servo, imu)

    # This is the main loop that will run until the shutdown method on the airbrakes is called
    while not airbrakes.shutdown_requested:
        airbrakes.update()


if __name__ == "__main__":
    main()

from Airbrakes.airbrakes import AirbrakesContext


class State:
    """
    For Airbrakes, we will have 4 states:
    1. Stand By - when the rocket is on the rail on the ground
    2. Motor Burn - when the motor is burning and the rocket is accelerating
    3. Flight - when the motor has burned out and the rocket is coasting, this is when air brakes will be deployed
    4. Free Fall - when the rocket is falling back to the ground after apogee, this is when the air brakes will be
    retracted
    """

    def __init__(self, context: AirbrakesContext):
        """
        :param context: The state context object that will be used to interact with the electronics
        """
        self.context = context

    def update(self):
        """
        Called every loop iteration. Uses the context to interact with the hardware and decides when to move to the
        next state.
        """
        pass

    def next_state(self):
        """
        We never expect/want to go back a state e.g. We're never going to go
        from Flight to Motor Burn, so this method just goes to the next state.
        """
        pass


class StandByState(State):
    """
    When the rocket is on the rail on the ground.
    """

    def update(self):
        pass

    def next_state(self):
        self.context.state = MotorBurnState(self.context)


class MotorBurnState(State):
    """
    When the motor is burning and the rocket is accelerating.
    """

    def update(self):
        pass

    def next_state(self):
        self.context.state = FlightState(self.context)


class FlightState(State):
    """
    When the motor has burned out and the rocket is coasting.
    """

    def update(self):
        pass

    def next_state(self):
        self.context.state = FreeFallState(self.context)


class FreeFallState(State):
    """
    When the rocket is falling back to the ground after apogee.
    """

    def update(self):
        pass

    def next_state(self):
        # Explicitly do nothing, there is no next state
        pass

import os
from typing import Tuple

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

# https://www.amazon.co.jp/dp/B01N1S3YJP/
CONTROLLER_JC_U4013S = "SHANWAN JC-U4013S DirectInput Mode"
CONTROLLER_HORI_RACING_WHEEL_APEX = "HORI Racing Wheel Apex"
CONTROLLERS = [CONTROLLER_JC_U4013S, CONTROLLER_HORI_RACING_WHEEL_APEX]

class GamePad:
    name: str
    j: pygame.joystick.Joystick

    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            raise ValueError("No joystick detected")
        j = pygame.joystick.Joystick(0)
        j.init()
        self.j = j
        self.name = j.get_name()

        # check if supported
        if self.name not in CONTROLLERS:
            raise ValueError("Unsupported controller")

    def close(self):
        self.j.quit()

    def get_values(self) -> Tuple[float, float]:
        """
        Returns a tuple of (speed, steering)
        """

        pygame.event.pump()

        if self.name == CONTROLLER_JC_U4013S:
            x = self.j.get_axis(0)
            y = self.j.get_axis(3) 
            if abs(x) < 0.1:
                x = 0
            if abs(y) < 0.1:
                y = 0
            return y, x
        if self.name == CONTROLLER_HORI_RACING_WHEEL_APEX:
            x = self.j.get_axis(0)

            accel = (self.j.get_axis(5) + 1) / 2
            brake = (self.j.get_axis(4) + 1) / 2
            y = -(accel - brake)
            if abs(y) < 0.1:
                y = 0

            return y, x

        raise ValueError("Unsupported controller")


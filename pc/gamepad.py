import os
import re
from typing import Tuple
from time import sleep


os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
from g29py import G29

# https://www.amazon.co.jp/dp/B01N1S3YJP/
CONTROLLER_HORI_RACING_WHEEL_APEX = "HORI Racing Wheel Apex"
CONTROLLER_JC_U4013S = "JC-U4013S"

CONTROLLERS = {
    CONTROLLER_JC_U4013S: "JC-U4013S DirectInput Mode$",
    CONTROLLER_HORI_RACING_WHEEL_APEX: "^HORI Racing Wheel Apex$",
}

class GamePad:
    name: str
    j: pygame.joystick.Joystick
    controller_index: int
    device: str
    g29: G29

    def __init__(self, device = "PYGAME") -> None:
        """
        Args:
            device: str, optional, name of the device to use ("PYGAME" or "G29")
        """

        self.device = device
        if device == "PYGAME":
            pygame.init()
            pygame.joystick.init()
            if pygame.joystick.get_count() == 0:
                raise ValueError("No joystick detected")

            for i in range(pygame.joystick.get_count()):
                j = pygame.joystick.Joystick(i)
                j.init()
                name = j.get_name()

                # check if supported
                for idx, pattern in CONTROLLERS.items():
                    if re.search(pattern, name):
                        self.j = j
                        self.name = name
                        self.controller_index = idx

            if not hasattr(self, 'name'):
                raise ValueError("Unsupported controller")

        elif device == "G29":
            for i in range(10):
                try:
                    self.name = "G29"
                    self.g29 = G29()
                    self.g29.set_range(400)
                    self.g29.set_autocenter(strength=0.9, rate=0.5)
                    break
                except Exception as e:
                    print(e)
                    print(f"Failed to connect to G29. Retrying... ({i})")
                    sleep(1)
                    continue
            else:
                raise RuntimeError("Failed to connect to G29")
        else:
            raise ValueError("Device must be either 'PYGAME' or 'G29'")

    def close(self):
        if self.device == "PYGAME":
            self.j.quit()

    def get_values(self) -> Tuple[float, float]:
        """
        Returns a tuple of (speed, steering)
        """

        if self.device == "PYGAME":
            pygame.event.pump()

            if self.controller_index == CONTROLLER_JC_U4013S:
                x = self.j.get_axis(0)
                y = self.j.get_axis(3) 
                if abs(x) < 0.1:
                    x = 0
                if abs(y) < 0.1:
                    y = 0
                return y, x
            if self.controller_index == CONTROLLER_HORI_RACING_WHEEL_APEX:
                x = self.j.get_axis(0)

                accel = (self.j.get_axis(5) + 1) / 2
                brake = (self.j.get_axis(4) + 1) / 2
                y = -(accel - brake)
                if abs(y) < 0.1:
                    y = 0

                return y, x

            raise ValueError("Unsupported controller")

        elif self.device == "G29":
            self.g29.pump()
            state = self.g29.get_state()
            steering = state["steering"]
            accel = state["accelerator"]
            brake = state["brake"]

            # update autocenter force
            self.g29.set_autocenter(strength=0.9, rate=(accel+1)/4 + 0.2)

            x = steering
            y = -(accel - brake) / 2
            if abs(y) < 0.1:
                y = 0

            return y, x


from dataclasses import dataclass
from threading import Thread
import time

# thrid party
import pygame

@dataclass
class State:
    self_ip: str | None = None
    target_ip: str | None = None
    batt_voltage: float = 0.0

    alive: bool = False
    batt_alarm: bool = False
    emergency_stop: bool = False

    throttle: float = 0.0
    steering: float = 0.0

    speed_level: int | None = None

    control_rtt_us: int | None = None


class UI:
    thread: Thread | None = None
    state: State

    def __init__(self, state: State):
        self.state = state
        self.screen = pygame.display.set_mode((400, 300)) 
        self.font = pygame.font.SysFont("Grobold", 40)
        self.font_small = pygame.font.SysFont("Grobold", 30)

        self.start()

    def update(self):
        if self.state.batt_alarm:
            self.screen.fill((255,0,0))
            text = self.font.render(f"Battery too low!", True, (255,255,255))
            self.screen.blit(text, [20, 100])

            text = self.font_small.render(f"Please charge the battery.", True, (255,255,255))
            self.screen.blit(text, [20, 150])
            pygame.display.update()
            return

        if self.state.emergency_stop:
            self.screen.fill((255,0,0))
            text = self.font.render(f"Emergency stop!", True, (255,255,255))
            self.screen.blit(text, [20, 100])

            text = self.font_small.render(f"Press R key to reset.", True, (255,255,255))
            self.screen.blit(text, [20, 150])
            pygame.display.update()
            return

        self.screen.fill((0,0,0))

        # horizontal axis
        pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(20, 180, 300, 30), width=2)
        pygame.draw.line(self.screen,
            (255,255,255),
            (20 + 150 + 150 * self.state.steering, 180),
            (20 + 150 + 150 * self.state.steering, 208),
            width=2,
        )

        # vertical axis
        pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(340, 30, 30, 180), width=2)
        pygame.draw.line(self.screen,
            (255,255,255),
            (340, 30 + 90 + 90 * self.state.throttle),
            (368, 30 + 90 + 90 * self.state.throttle),
            width=2,
        )

        # battery
        text = self.font_small.render(f"Battery", True, (255,255,255))
        self.screen.blit(text, [20, 220])

        if self.state.batt_voltage is not None:
            text = self.font.render(
                f"{self.state.batt_voltage:.2f} V",
                True,
                (255,255,255),
            )
        else:
            text = self.font.render(
                f"-",
                True,
                (255,255,255),
            )

        self.screen.blit(text, [20, 250])

        # RTT
        rtt_us = self.state.control_rtt_us
        if rtt_us is not None:
            rtt = rtt_us / 1000.0
            text = self.font_small.render(f"RTT: {rtt:.2f} ms", True, (255,255,255))
            self.screen.blit(text, [20, 100])

        # alive
        if self.state.alive:
            pygame.draw.circle(self.screen, (0,255,0), (280, 45), 30)
        else:
            pygame.draw.circle(self.screen, (255,0,0), (280, 45), 30)

        text = self.font_small.render(f"VTX: {self.state.target_ip}", True, (255,255,255))
        self.screen.blit(text, [20, 20])

        # speed level
        text = self.font_small.render(f"Speed: Lv.{self.state.speed_level}", True, (255,255,255))
        self.screen.blit(text, [20, 50])

        pygame.display.update()

    def start(self):
        self.thread = Thread(target=self._start)
        self.thread.daemon = True
        self.thread.start()

    def _start(self):
        while True:
            self.update()
            time.sleep(0.1)

    def close(self):
        if self.thread is not None:
            self.thread.join()


import pygame
from time import sleep

def main():
    pygame.init()
    j = pygame.joystick.Joystick(0)
    j.init()
    print("Controller: " + j.get_name())

    try:
        while True:
            events = pygame.event.pump()
            for i in range(j.get_numaxes()):
                print(f"Axis {i}: {j.get_axis(i)}")
            for i in range(j.get_numbuttons()):
                print(f"Button {i}: {j.get_button(i)}")

            sleep(0.1)

    except KeyboardInterrupt:
        j.quit()

if __name__ == '__main__':
    main()


from time import sleep

import gamepad

if __name__ == "__main__":
    gp = gamepad.GamePad()
    print("Controller connected:", gp.name)
    while True:
        # Get the values
        speed, steering = gp.get_values()
        print(f"Speed: {speed}, Steering: {steering}")
        # Do something with the values
        sleep(0.1)
        pass



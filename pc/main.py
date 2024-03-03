from os import environ
from time import sleep, time
import argparse

import serial
import serial.tools.list_ports

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
environ['SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS'] = '1'
import pygame

from shunkei_sdk import ShunkeiVTX

# local import
from gamepad import GamePad
from ui import State, UI

DEFAULT_PORT = 12334

center_steer = 90
steer_trim = 0

last_called_dict = {}
def throttle(interval, key):
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            global last_called_dict
            last_called = last_called_dict.get(key, 0)
            if time.time() - last_called < interval:
                return
            last_called_dict[key] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

def serial_auto_connect() -> serial.Serial:
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "Pico" in p.description:
            print("Connecting to Pico...: ", p.device)
            return serial.Serial(p.device)
    else:
        raise IOError("No Pico found")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="host name")
    parser.add_argument("-s", "--speed", type=int, default=5, help="max speed adjustment")
    parser.add_argument("-w", "--webrtc", action="store_true", help="use webrtc")
    parser.add_argument("--room-id", help="room id")
    parser.add_argument("--serial", action="store_true", help="use serial")
    parser.add_argument("--voltage", type=float, default=6.0, help="battery voltage lower limit")
    args = parser.parse_args()

    pygame.init()
    pygame.font.init()

    if args.serial:
        ser = serial_auto_connect()

    gp = GamePad()
    print(f"Joystick: {gp.name}")

    state = State()
    ui = UI(state)

    state.speed_level = args.speed
    alive = False
    batt_voltage = 0
    batt_voltage_below_cnt = 0
    batt_alarm = False

    # exponential backoff
    vtx: ShunkeiVTX | None = None
    while True:
        sleep(1)
        try:
            # set up host and port
            if args.webrtc:
                roomId = args.room_id
                if roomId is None:
                    print("room id must be specified when using webrtc")
                    parser.print_help()
                    exit(1)
                vtx = ShunkeiVTX.connect_via_webrtc(roomId)
                print(f"Connected to room {roomId} via webrtc")
            elif args.host is None:
                vtx = ShunkeiVTX.auto_connect()
                print(f"device found: {vtx.host}")
            elif ":" in args.host:
                host, port = args.host.split(":")
                vtx = ShunkeiVTX.connect_via_ip(host, int(port))
            else:
                vtx = ShunkeiVTX.connect_via_ip(args.host, DEFAULT_PORT)

            last_keep_alive = 0

            print("Waiting for input...")
            while True:
                buf = vtx.uart_read(1024)
                if buf is not None:
                    lines = buf.decode().split("\n")
                    for line in lines:
                        line = line.strip()
                        if line == "":
                            continue
                        if line == "k":
                            last_keep_alive = time()
                        else:
                            if line.startswith("batt:"):
                                try:
                                    batt_voltage = float(line.split(":")[1])
                                    state.batt_voltage = batt_voltage
                                except ValueError:
                                    pass

                if time() - last_keep_alive > 1:
                    alive = False
                else:
                    alive = True
                state.alive = alive

                if args.serial:
                    if ser.in_waiting > 0:
                        buf = ser.readline().decode('utf-8').strip()
                        try:
                            val = int(buf)
                            state.speed_level = val
                        except ValueError:
                            pass

                events = pygame.event.get()
                for event in events:
                    # keyboard
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            if state.speed_level < 10:
                                state.speed_level += 1
                        elif event.key == pygame.K_DOWN:
                            if state.speed_level > 1:
                                state.speed_level -= 1
                        elif event.key == pygame.K_1:
                            state.speed_level = 1
                        elif event.key == pygame.K_2:
                            state.speed_level = 2
                        elif event.key == pygame.K_3:
                            state.speed_level = 3
                        elif event.key == pygame.K_4:
                            state.speed_level = 4
                        elif event.key == pygame.K_5:
                            state.speed_level = 5
                        elif event.key == pygame.K_6:
                            state.speed_level = 6
                        elif event.key == pygame.K_7:
                            state.speed_level = 7
                        elif event.key == pygame.K_8:
                            state.speed_level = 8
                        elif event.key == pygame.K_9:
                            state.speed_level = 9
                        elif event.key == pygame.K_0:
                            state.speed_level = 10
                    elif event.type == pygame.QUIT:
                        raise KeyboardInterrupt()
                events = pygame.event.pump()

                y, x = gp.get_values()
                steer = center_steer + (15*x) + steer_trim
                speed = 90 + (15*y) * state.speed_level / 10

                # update state
                state.steering = x
                state.throttle = y

                if not batt_alarm:
                    vtx.uart_write(f"{int(steer)} {int(speed)} \n".encode())

                # check battery voltage. if it is too low, stop the car.
                # battery may be lower than the limit when the car is running, so we need to check it for a while.
                if batt_voltage < args.voltage:
                    batt_voltage_below_cnt += 1
                    if batt_voltage_below_cnt > 10:
                        # TODO: shutdown the car
                        batt_alarm = True
                        state.batt_alarm = True
                else:
                    batt_voltage_below_cnt = 0
                    batt_alarm = False
                    state.batt_alarm = False

                state.control_rtt_us = vtx.control_rtt_us
                state.target_ip = vtx.host

                @throttle(0.5, "update_serial")
                def update_serial():
                    if args.serial:
                        if alive:
                            ser.write(b"r")
                            #ser.flush()
                        else:
                            ser.write(b"s")
                            #ser.flush()

                update_serial()

                sleep(0.01)

        except KeyboardInterrupt:
            print()
            print("Exiting...")
            if vtx is not None:
                vtx.close()
            gp.close()
            print("Exited...")
            exit(0)
        except:
            #raise # for debug
            sleep(1)
            print()
            print("Connection closed. Reconecting...")
            continue


if __name__ == '__main__':
    main()


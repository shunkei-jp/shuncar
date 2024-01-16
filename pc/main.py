from os import environ
from time import sleep, time
import argparse

import serial
import serial.tools.list_ports

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

from gamepad import GamePad

from shunkei_sdk import ShunkeiVTX

DEFAULT_PORT = 12334

center_steer = 93.3
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
    args = parser.parse_args()

    speed_level = args.speed
    alive = False

    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont("Grobold", 40)
    screen = pygame.display.set_mode((400, 300)) 

    if args.serial:
        ser = serial_auto_connect()

    gp = GamePad()
    print(f"Joystick: {gp.name}")

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
                buf = vtx.read(1024)
                if buf is not None:
                    lines = buf.decode().split("\n")
                    for line in lines:
                        line = line.strip()
                        if line == "":
                            continue
                        if line == "k":
                            last_keep_alive = time()

                if time() - last_keep_alive > 0.1:
                    alive = False
                else:
                    alive = True

                if args.serial:
                    if ser.in_waiting > 0:
                        buf = ser.readline().decode('utf-8').strip()
                        try:
                            val = int(buf)
                            speed_level = val
                        except ValueError:
                            pass

                events = pygame.event.get()
                for event in events:
                    # keyboard
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            if speed_level < 10:
                                speed_level += 1
                        elif event.key == pygame.K_DOWN:
                            if speed_level > 1:
                                speed_level -= 1
                        elif event.key == pygame.K_1:
                            speed_level = 1
                        elif event.key == pygame.K_2:
                            speed_level = 2
                        elif event.key == pygame.K_3:
                            speed_level = 3
                        elif event.key == pygame.K_4:
                            speed_level = 4
                        elif event.key == pygame.K_5:
                            speed_level = 5
                        elif event.key == pygame.K_6:
                            speed_level = 6
                        elif event.key == pygame.K_7:
                            speed_level = 7
                        elif event.key == pygame.K_8:
                            speed_level = 8
                        elif event.key == pygame.K_9:
                            speed_level = 9
                        elif event.key == pygame.K_0:
                            speed_level = 10
                    elif event.type == pygame.QUIT:
                        raise KeyboardInterrupt()
                events = pygame.event.pump()

                y, x = gp.get_values()
                steer = center_steer + (15*x) + steer_trim
                speed = 90 + (15*y) * speed_level / 10

                vtx.write(f"{int(steer)} {int(speed)} \n".encode())

                @throttle(0.1, "update_caption")
                def update_caption():
                    print(f"\r[{'alive' if alive else 'dead'}] steer:{steer:.2f}, speed:{speed:.2f} (level: {speed_level})", end=" ")
                    pygame.display.set_caption(f"[{'alive' if alive else 'dead'}] steer:{steer:.2f}, speed:{speed:.2f} (level: {speed_level})")

                    screen.fill((0,0,0))

                    text = font.render(f"Level: {speed_level}", True, (255,255,255))
                    screen.blit(text, [20, 100])

                    if alive:
                        pygame.draw.circle(screen, (0,255,0), (200, 200), 50)
                    else:
                        pygame.draw.circle(screen, (255,0,0), (200, 200), 50)

                    pygame.display.update()

                @throttle(0.5, "update_serial")
                def update_serial():
                    if args.serial:
                        if alive:
                            ser.write(b"r")
                            #ser.flush()
                        else:
                            ser.write(b"s")
                            #ser.flush()

                update_caption()
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


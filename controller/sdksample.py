from time import sleep
from shunkei_sdk import ShunkeiVTX

def main():
    vtx = ShunkeiVTX.auto_connect()
    while True:
        steer = 93.3
        speed = 95
        vtx.write(f"{int(steer)} {int(speed)} \n".encode())
        sleep(0.01)
        data = vtx.read(1024)
        if data:
            print(data.decode(), end="")


if __name__ == "__main__":
    main()


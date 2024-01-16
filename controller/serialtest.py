import serial
import serial.tools.list_ports

def main():
    ser = auto_connect()
    while True:
        s = ser.readline().decode('utf-8').strip()
        print(s)

def auto_connect() -> serial.Serial:
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "Pico" in p.description:
            print("Connecting to Pico...: ", p.device)
            return serial.Serial(p.device)
    else:
        raise IOError("No Pico found")

if __name__ == '__main__':
    main()

import serial
import time
from datetime import datetime

# File path for logging
file_path = "../server/history.txt"

try:
    arduino = serial.Serial(port='/dev/cu.usbmodem11401', baudrate=115200, timeout=.1)
    time.sleep(2)  # Let connection settle
except serial.SerialException as e:
    print(f"Error: {e}")
    exit()

with open(file_path, "a") as file:
    while True:
        try:
            data = arduino.readline().decode('ascii').rstrip()  # Read the data, decode, and strip
            if data:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_entry = f"{timestamp} {data}\n"
                print(log_entry, end="")  # Print to console
                file.write(log_entry)
                file.flush()  # Ensure data is written immediately
        except serial.SerialException as e:
            print(f"Error reading from serial port: {e}")
            break
        except ValueError as e:
            print(f"Decoding error: {e}")
        except KeyboardInterrupt:
            print("Exiting program")
            break

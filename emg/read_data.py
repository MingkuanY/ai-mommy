import serial
import time
from datetime import datetime
from collections import deque
import numpy as np

# File path for logging
file_path = "../server/history.txt"

# Initialize deque with max length of 1000 for rolling average
data_window = deque(maxlen=1000)


def calculate_rolling_average():
    if not data_window:
        return None
    return np.mean(data_window)


try:
    arduino = serial.Serial(port='/dev/cu.usbmodem11401',
                            baudrate=115200, timeout=.1)
    time.sleep(2)  # Let connection settle
except serial.SerialException as e:
    print(f"Error: {e}")
    exit()

with open(file_path, "a") as file:
    while True:
        try:
            # Read the data, decode, and strip
            data = arduino.readline().decode('ascii').rstrip()
            if data:
                try:
                    # Convert data to float and add to rolling window
                    numeric_data = float(data)
                    data_window.append(numeric_data)

                    # Calculate rolling average
                    rolling_avg = calculate_rolling_average()

                    # Create log entry with both raw data and rolling average
                    timestamp = datetime.now().strftime("%s")
                    log_entry = f"{timestamp} {rolling_avg:.2f} {numeric_data}\n"

                    print(log_entry, end="")  # Print to console
                    file.write(log_entry)
                    file.flush()  # Ensure data is written immediately

                except ValueError as e:
                    print(f"Error converting data to float: {data}")

        except serial.SerialException as e:
            print(f"Error reading from serial port: {e}")
            break
        except KeyboardInterrupt:
            print("Exiting program")
            break

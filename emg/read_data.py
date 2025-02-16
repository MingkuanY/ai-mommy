import serial
import time
from datetime import datetime
from collections import deque
import numpy as np
import statistics

# File path for logging
file_path = "../server/history.txt"

# Initialize deque with max length of 1000 for rolling average
data_window = deque(maxlen=500)
data_window_max = deque(maxlen=5000)
output_every = 500
current_output_index = 0



def put_stress_level(stress_levels):
    stress_level = np.percentile(list(stress_levels), 75)
    # stress_level = max(stress_levels)
    stress_out = None
    if stress_level  > 0 and stress_level < 100:
        stress_out=  "Low stress"
    elif stress_level > 100 and stress_level < 200:
        stress_out =  "Normal but not low stress"
    elif stress_level > 200 and stress_level < 300:
        stress_out =  "Moderately high stress"
    elif stress_level > 300 and stress_level < 400:
        stress_out =  "Very High stress"
    else:
        stress_out = "EXTREMELY high stress"

    with open("../stress.txt", "w") as f:
        f.write(stress_out)
    

def calculate_rolling_average():
    if not data_window:
        return None
    return np.mean(data_window)


try:
    arduino = serial.Serial(port='/dev/cu.usbmodem21401',
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
                    data_window_max.append(numeric_data)
                    put_stress_level(data_window_max)

                    # Calculate rolling average
                    rolling_avg = calculate_rolling_average()

                    # Create log entry with both raw data and rolling average
                    timestamp = datetime.now().strftime("%s")
                    log_entry = f"{timestamp} {rolling_avg:.2f} {numeric_data}\n"

                    if current_output_index == 0:
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




        current_output_index += 1
        current_output_index %= output_every



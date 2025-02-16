import serial
import time
from datetime import datetime
from collections import deque
import numpy as np
import threading

# File paths
file_path = "../server/history.txt"
shock_file_path = "../shock.txt"
stress_file_path = "../stress.txt"

# Initialize deque with max length of 1000 for rolling average
data_window = deque(maxlen=500)
data_window_max = deque(maxlen=5000)
output_every = 500
current_output_index = 0
shock_status = False

def put_stress_level(stress_levels):
    stress_level = np.percentile(list(stress_levels), 75)
    stress_out = ""
    if 0 < stress_level < 100:
        stress_out = "Low stress"
    elif 100 <= stress_level < 200:
        stress_out = "Normal but not low stress"
    elif 200 <= stress_level < 300:
        stress_out = "Moderately high stress"
    elif 300 <= stress_level < 400:
        stress_out = "Very High stress"
    else:
        stress_out = "EXTREMELY high stress"
    
    with open(stress_file_path, "w") as f:
        f.write(stress_out)

def calculate_rolling_average():
    if not data_window:
        return None
    return np.mean(data_window)

def check_shock_status():
    global shock_status
    while True:
        try:
            with open(shock_file_path, "r") as f:
                content = f.read().strip().lower()
                shock_status = content == "true"
        except FileNotFoundError:
            shock_status = False
        time.sleep(0.2)

try:
    arduino = serial.Serial(port='/dev/cu.usbmodem21401',
                            baudrate=115200, timeout=0.1)
    time.sleep(2)  # Let connection settle
except serial.SerialException as e:
    print(f"Error: {e}")
    exit()

# Start shock status monitoring in a separate thread
shock_thread = threading.Thread(target=check_shock_status, daemon=True)
shock_thread.start()

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
                
                except ValueError:
                    print(f"Error converting data to float: {data}")
            
            # Send "ON" if shock status is true
            if shock_status:
                arduino.write(b"ON\n")
                shock_status = False
                print("Sent: ON")

        except serial.SerialException as e:
            print(f"Error reading from serial port: {e}")
            break
        except KeyboardInterrupt:
            print("Exiting program")
            break

        current_output_index += 1
        current_output_index %= output_every

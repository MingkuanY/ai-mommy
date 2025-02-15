import serial
import time

try:
  arduino = serial.Serial(port='/dev/cu.usbmodem1401', baudrate=115200, timeout=.1)
  time.sleep(2) #let connection settle
except serial.SerialException as e:
  print(f"Error: {e}")
  exit()

while True:
  try:
    data = arduino.readline().decode('ascii').rstrip() # Read the data, decode, and strip
    if data:
      print(data) # Print the data
  except serial.SerialException as e:
    print(f"Error reading from serial port: {e}")
    break
  except ValueError as e:
    print(f"Decoding error: {e}")
  except KeyboardInterrupt:
    print("Exiting program")
    break
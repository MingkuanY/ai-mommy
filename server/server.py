from threading import Thread
from flask import Flask, jsonify
from flask_cors import CORS
import random
from time import sleep

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'


HISTORY_FILE = "history.txt"  # Change this to the actual file path


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route("/history", methods=["GET"])
def get_history():
    try:

        # Read the existing numbers from the file
        data = read_history()

        # numbers = numbers

        # Convert the numbers into the required Recharts format
        data = [
            {
                "time": time,
                "stress": stress
            }
            for time, stress in data
        ]

        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "History file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def add_random_number():
    while True:
        # print("Adding random number")

        # Read the existing numbers from the file
        data = read_history()

        if len(data) > 20:
            data.pop(0)

        latest_time = data[-1][0]

        # Add a new random number
        new_time = latest_time + 1
        new_stress = random.randint(0, 100)
        data.append([new_time, new_stress])

        # Write back the updated numbers
        with open(HISTORY_FILE, "w") as file:
            for time, stress in data:
                file.write(f"{time} {stress}\n")

        sleep(1)  # Add a number every second


def read_history():
    # formatted as time stress with space in between
    with open(HISTORY_FILE, "r") as file:
        data = []
        for line in file:
            data.append([int(x) for x in line.strip().split()])
    return data


if __name__ == "__main__":
    # Start a thread to add random numbers to the history file
    # thread = Thread(target=add_random_number)
    # thread.start()

    # Binds to all available network interfaces
    app.run(host="0.0.0.0", port=5000, debug=False)

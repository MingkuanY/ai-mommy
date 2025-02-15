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
        with open(HISTORY_FILE, "r") as file:
            numbers = [int(line.strip())
                       for line in file if line.strip().isdigit()]

        # numbers = numbers

        # Convert the numbers into the required Recharts format
        data = [
            {
                "name": str(i),  # Use index as the name
                "stress": num
            }
            for i, num in enumerate(numbers)
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
        numbers = []
        try:
            with open(HISTORY_FILE, "r") as file:
                for line in file:
                    if line.strip().isdigit():
                        numbers.append(int(line.strip()))
        except FileNotFoundError:
            pass  # If file doesn't exist, start fresh

        # Ensure at most 30 numbers
        if len(numbers) >= 20:
            numbers.pop(0)

        # Add a new random number
        numbers.append(random.randint(0, 10))

        # Write back the updated numbers
        with open(HISTORY_FILE, "w") as file:
            content = "\n".join(str(num) for num in numbers)
            # print(content)
            file.write(content + "\n")  # Ensure newline at end for readability

        sleep(1)  # Add a number every second


if __name__ == "__main__":
    # Start a thread to add random numbers to the history file
    thread = Thread(target=add_random_number)
    thread.start()

    # Binds to all available network interfaces
    app.run(host="0.0.0.0", port=5000, debug=False)

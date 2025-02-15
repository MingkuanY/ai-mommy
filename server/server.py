from flask import Flask, jsonify
from flask_cors import CORS

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


if __name__ == "__main__":
    # Binds to all available network interfaces
    app.run(host="0.0.0.0", port=5000, debug=True)

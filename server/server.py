
from threading import Thread
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import random
from time import sleep
from dotenv import load_dotenv
from openai import OpenAI

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'

load_dotenv()
openai_client = OpenAI()


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


# post for adding a query
@app.route("/ask", methods=["POST"])  # todo: remove get
def handle_query():
    # message = request.json["message"]
    history = request.json["history"]

    # history looks like array of
    #     interface ChatObject {
    # 	sender: "user" | "mommy";
    # 	message: string;
    # }

    # map history to openai message format
    messages = [
        {"role": "system", "content": "You are an anime mommy that tries to make the user feel comforted in conversation. Talk like an anime mommy discord ekitten."},
    ]
    for chat in history:
        role = "user" if chat["sender"] == "user" else "assistant"
        messages.append({"role": role, "content": chat["message"]})

    def generate_response():
        stream = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    # Wrap the generator in a Response and set the mimetype
    return Response(generate_response(), mimetype='text/plain')

# def handle_query():
#     # has query in the body
#     query = request.json["query"]

#     def generate_response():
#         stream = openai_client.chat.completions(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are an anime mommy that tries to make the user feel comforted in conversation. Talk like an anime mommy discord ekitten."},
#                 {"role": "user", "content": query},
#             ],
#             max_tokens=150,
#             stream=True
#         )

#         for chunk in stream:
#             if chunk.choices[0].delta.content is not None:
#                 yield (chunk.choices[0].delta.content)

#     return "hi", {'Content-Type': 'text/plain'}
    # return generate_response(), {'Content-Type': 'text/plain'}

    # response = Response(generate_response(), content_type="text/plain")
    # response.headers.add("Access-Control-Allow-Origin", "*")
    # response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    # response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")

    # return response


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
    app.run(host="0.0.0.0", port=5000, debug=True)

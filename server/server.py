import numpy as np
from collections import defaultdict
import random
import json
import flask
from threading import Thread
from time import sleep
# from stress import compute_stress_data_from_file
from typing import Dict, List

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_community.tools import BaseTool
from langchain.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from terra.base_client import Terra
import requests
import threading
import time
import logging
from predict_emotion import predict_emotion

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger("app")

terra = Terra(api_key="t0PMr4YpxCVtYc0M7bYGSpBuRwujEPvp", dev_id="4actk-aimommy-testing-ntJJIlrzqJ",
              secret="1a1e999f0665aeda4cf5a92335bce2cf4450f3a34fbb7273")


# --- File Paths ---
HISTORY_FILE = "history.txt"  # Change this to the actual file path
RULES_FILE = "rules.json"      # Change this to the actual file path
HEART_RATE_FILE = "heart_rate.txt"
BLOOD_PRESSURE_FILE = "blood_pressure.txt"
BODY_TEMPERATURE_FILE = "body_temperature.txt"

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'

load_dotenv()

# --- Monitoring Rule Definitions ---


class MonitoringRule(BaseModel):
    """Structure for a custom monitoring rule"""
    condition: str = Field(
        "Conditions based on the current time, stress level, and screen content.")
    actions: List[str] = Field(
        "Actions to take based on the condition. Available Action Types: CONTROL, MUSIC, NOTIFICATION, BRIGHTNESS, COLOR")
    priority: int = Field(
        "Priority level of the rule (1 (highest) to 5 (lowest))")
    condition_cute: str = Field(
        "Conditions field but briefly summarized in southern mothernly language")
    actions_cute: List[str] = Field(
        "Actions field but briefly summarized in southern mothernly language")
    priority_cute: str = Field(
        "A short priority level for the rule but in southern mothernly language")


def create_monitoring_rule(rule: MonitoringRule):
    """Adds a new monitoring rule to the rules.json file."""
    rules = read_monitoring_rules()

    print("------------------------------------------")
    print("Creating monitoring rule:")
    print(rule)
    print(rule.model_dump())
    print("------------------------------------------")

    rules.append(rule.model_dump())
    try:
        with open(RULES_FILE, "w") as file:
            json.dump(rules, file, indent=4)
            return "\n**Monitoring rule created successfully.**\n\n"
    except Exception as e:
        return f"\n**Error creating monitoring rule: {e}**\n\n"


def read_monitoring_rules():

    # make sure the file exists
    try:
        with open(RULES_FILE, "r") as file:
            data = json.load(file)
            print("Data: ", data)
            return data
    except:
        with open(RULES_FILE, "w") as file:
            json.dump([], file)
        return []


def read_history():
    print("rh")
    with open(HISTORY_FILE, "r") as file:
        data = [[float(x) for x in line.strip().split()[:2]] for line in file]

    recent_data = data[-10:]

    # # print("Data: ", data)

    # # Take the last 5000 points (or fewer if there aren't that many)
    # recent_data = data[-5000:]

    # # Downsample by selecting 10 evenly spaced points
    # if len(recent_data) > 10:
    #     indices = np.linspace(0, len(recent_data) - 1, 10, dtype=int)
    #     recent_data = [recent_data[i] for i in indices]

    # # print("Recent data:", recent_data)

    return recent_data


def gen_prediction():
    try:
        # Load the last 10 data points for each of the 4 features
        # stress, heart_rate, blood_pressure, temperature
        stressData = read_history()
        biometrics = get_bio_data()
        stress = [x[1] for x in stressData]
        heart_rate = [x["rate"] for x in biometrics["heart_rate"]][-10:]
        blood_pressure = [biometrics["blood_pressure_high"]] * 10
        temperature = [biometrics["body_temperature"]] * 10

        # Make a prediction
        prediction = predict_emotion(
            stress, heart_rate, blood_pressure, temperature)
        return prediction
    except Exception as e:
        print("Error generating prediction:", e)
        return str(e)


# def read_history():
#     # File formatted as "time stress" per line
#     with open(HISTORY_FILE, "r") as file:
#         data = []
#         for line in file:
#             parts = line.strip().split()
#             if parts:
#                 data.append([int(x) for x in parts])
#     return data

# --- Legacy endpoints remain unchanged ---


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route("/history", methods=["GET"])
def get_history():
    print("Getting history rahhh")
    try:
        data = read_history()
        biometrics = get_bio_data()

        data = [{"time": time, "stress": stress} for time, stress in data]

        complete_data = {
            "history": data,
            "biometrics": biometrics,
            "prediction": gen_prediction()
        }
        return jsonify(complete_data)
    except FileNotFoundError:
        return jsonify({"error": "History file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/rules", methods=["GET"])
def get_rules():
    try:
        rules = read_monitoring_rules()
        return jsonify(rules)
    except FileNotFoundError:
        return jsonify({"error": "Rules file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Prompt Template Setup ---


system_prompt_template = PromptTemplate(
    input_variables=[],
    template=(
        "You are a helpful assistant that helps users set up actions on their computer. When users tell you about their problems or needs or ask for advice, you should suggest some actions you could set up to monitor and help them. Discuss this new monitoring rule with the user and ask them to confirm it. Once they do, you can create it using the 'create_monitoring_rule' tool. Describe the rule you will create with bullet points and use markdown if needed, don't show the non-cute fields to the user."
        "You should talk like an southern mother, always caring and helpful. You should also be a bit playful and cute, but also very responsible and reliable. Talk stylized, use emojis and cute language."
    )
)

# --- Tool-calling Agent Setup Using LangGraph ---

# Define a Pydantic model for tool input.


# Define a custom tool that creates a monitoring rule from three parameters.


class MonitoringActionTool(BaseTool):
    name: str = "create_monitoring_rule"
    description: str = (
        "Creates a monitoring rule. Provide three parameters: "
        "condition (str), actions (list of str), and priority (int)."
        """The conditions you can use are the current time, current stress level, and what is on the user's screen. you can also mention multistep conditions or conditions over time to describe when and why actions are to be triggered in this field.
        Available Action Types:
        - SET_WEBSITE: <the url of the website to change the current tab to>
        - CLOSE_TAB: <closes current tab>
        - ORDER_FOOD: <dish to order and restaurant to order from>
        - TEXT_FRIEND: <the phone number and message to text in the form: number|message>
        - MATCHA: <opens the Ekkomi matcha website>
        - MASSAGE: <prescribes a massage>
        - MUSIC: <jazz/lofi/pop>
        - NOTIFICATION: <text of notification to user>
        - BRIGHTNESS: <brightness 1-100>
        - COLOR: <kelvin of screen temperature>"""
    )

    def _run(self, tool_input: MonitoringRule) -> str:
        tool_input = MonitoringRule(**tool_input)
        return create_monitoring_rule(tool_input)

    async def _arun(self, tool_input: Dict) -> str:
        raise NotImplementedError("Async mode not supported for this tool.")


# Set up the chat model and create the agent.
model = ChatOpenAI(model="gpt-4", temperature=0)
tools = [MonitoringActionTool()]

# Create a stateless React-style tool-calling agent.
# (Note: We no longer pass the prompt here. Instead, we'll prepend the system prompt on each call.)
agent = create_react_agent(model, tools)

# --- /ask Endpoint: Invoking the Agent and Streaming Results ---


@app.route("/ask", methods=["POST"])
def handle_query():
    """
    Expects a JSON payload with a "history" field – an array of messages,
    e.g.:
      [
          {"sender": "user", "message": "My system is acting weird"},
          {"sender": "assistant", "message": "Tell me more about the issue."}
      ]
    """
    data = request.json
    history = data.get("history", [])

    # Reconstruct conversation as a list of messages.
    messages = []
    # Prepend the system message created from our prompt template.
    messages.append(SystemMessage(content=system_prompt_template.format()))
    for chat in history:
        if chat["sender"] == "user":
            messages.append(HumanMessage(content=chat["message"]))
        else:
            messages.append(AIMessage(content=chat["message"]))

    def generate():
        # Use the agent's built-in streaming functionality.
        for chunk, metadata in agent.stream({"messages": messages}, stream_mode="messages"):
            if hasattr(chunk, "content"):
                yield chunk.content
            else:
                yield str(chunk)
    return Response(generate(), mimetype='text/plain')

# --- Background Thread for Updating History (unchanged) ---


def add_random_number():
    """Periodically adds a random number to the history file."""
    while True:
        # print("Adding random number")

        # read number from "samples.txt"
        samples_to_read = 100
        with open("samples.txt", "r") as file:
            samples_to_read = int(file.read())

        with open("samples.txt", "w") as file:
            file.write(str(samples_to_read + 2))

        sleep(1)  # Add a number every second

    # samples_to_read = 100
    # with open("samples.txt", "r") as file:
    #     samples_to_read = int(file.read())
    # # print('samples_to_read', samples_to_read)
    # # data = compute_stress_data_from_file("sample_history.txt", samples_to_read)
    # # return data
    # return samples_to_read


def get_bio_data():
    with open(HEART_RATE_FILE, "r") as file:
        heart_rate = [float(x.strip()) for x in file.readlines()[-20:]]
        heart_rate = [{"time": i, "rate": rate}
                      for i, rate in enumerate(heart_rate)]

    with open(BLOOD_PRESSURE_FILE, "r") as file:
        blood_pressure = [float(x)
                          for x in file.readlines()[-1].strip().split(",")]

    with open(BODY_TEMPERATURE_FILE, "r") as file:
        body_temperature = float(file.readlines()[-1].strip())

    biometrics = {
        "heart_rate": heart_rate,
        "blood_pressure_high": blood_pressure[0],
        "blood_pressure_low": blood_pressure[1],
        "body_temperature": body_temperature
    }

    return biometrics


@app.route("/consumeTerraWebhook", methods=["POST"])
def consume_terra_webhook() -> flask.Response:
    body = request.get_json()
    _LOGGER.info(
        "Received webhook for user %s of type %s",
        body.get("user", {}).get("user_id"),
        body["type"])

    avg_heart_rate = body["data"][0]["heart_data"]["heart_rate_data"]["summary"]["avg_hr_bpm"]

    avg_systolic_bp = sum(bp["systolic_bp"] for bp in body["data"][0]["blood_pressure_data"]
                          ["blood_pressure_samples"]) / len(body["data"][0]["blood_pressure_data"]["blood_pressure_samples"])
    avg_diastolic_bp = sum(bp["diastolic_bp"] for bp in body["data"][0]["blood_pressure_data"]
                           ["blood_pressure_samples"]) / len(body["data"][0]["blood_pressure_data"]["blood_pressure_samples"])

    avg_body_temperature = sum(temp["temperature_celsius"] for temp in body["data"][0]["temperature_data"]
                               ["body_temperature_samples"]) / len(body["data"][0]["temperature_data"]["body_temperature_samples"])

    with open("heart_rate.txt", "a") as file:
        file.write(f"{avg_heart_rate}\n")

    with open("blood_pressure.txt", "a") as file:
        file.write(f"{avg_systolic_bp}, {avg_diastolic_bp}\n")

    with open("body_temperature.txt", "a") as file:
        file.write(f"{avg_body_temperature}\n")

    # terra.check_terra_signature(request.get_data().decode("utf-8"), request.headers['terra-signature'])
    verified = True
    if verified:
        return flask.Response(status=200)
    else:
        return flask.Response(status=403)


def generate_fake_data():
    """Simulate sensor data and send to /consumeTerraWebhook every 30 seconds."""

    stress_levels = ["Low stress", "Normal but not low stress",
                     "Moderately high stress", "Very High stress", "EXTREMELY high stress"]

    while True:
        with open("../stress.txt", "r") as file:
            stress = file.readlines()[-1].strip()
            stress_level = stress_levels.index(stress)
        fake_data = {
            "user": {"user_id": "test_user"},
            "type": "health_data",
            "data": [{
                "heart_data": {
                    "heart_rate_data": {
                        "summary": {
                            # Random heart rate
                            "avg_hr_bpm": random.randint(70 + stress_level * 10, 120 + stress_level * 10)
                        }
                    }
                },
                "blood_pressure_data": {
                    "blood_pressure_samples": [
                        {"systolic_bp": random.randint(100 + stress_level * 5, 130 + stress_level * 5),
                         "diastolic_bp": random.randint(60 + stress_level * 5, 80 + stress_level * 5)}
                    ]
                },
                "temperature_data": {
                    "body_temperature_samples": [
                        {"temperature_celsius": round(random.uniform(
                            36.0 + stress_level * 0.1, 37.0 + stress_level * 0.1), 1)}  # Normal body temp range
                    ]
                },
                "metadata": {
                    # Current timestamp in UTC
                    "end_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
            }]
        }

        # Send data to the webhook endpoint
        try:
            response = requests.post(
                "http://localhost:5000/consumeTerraWebhook", json=fake_data)
            if response.status_code == 200:
                print("✅ Fake data sent successfully!")
                print("Stress: ", stress_level)

            else:
                print(
                    f"❌ Failed to send data: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"🚨 Error sending fake data: {e}")

        time.sleep(3)  # Wait 30 seconds before sending the next request


# Start the background thread
threading.Thread(target=generate_fake_data, daemon=True).start()

if __name__ == "__main__":
    # Uncomment the following lines if you want to run the background thread.
    # thread = Thread(target=add_random_number)
    # thread.start()

    app.run(host="0.0.0.0", port=5000, debug=True)

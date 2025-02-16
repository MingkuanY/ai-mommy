import numpy as np
from collections import defaultdict
import random
import json
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

# --- File Paths ---
HISTORY_FILE = "history.txt"  # Change this to the actual file path
RULES_FILE = "rules.json"      # Change this to the actual file path

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
        "Conditions field but briefly summarized in cute discord ekitten anime mommy language")
    actions_cute: List[str] = Field(
        "Actions field but briefly summarized in cute discord ekitten anime mommy language")
    priority_cute: str = Field(
        "A short priority level for the rule but in cute discord ekitten anime mommy language")


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
        data = [{"time": time, "stress": stress} for time, stress in data]
        return jsonify(data)
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
        "You are a helpful assistsant that helps users set up actions on their computer. When users tell you about their problems or needs or ask for advice, you should suggest some actions you could set up to monitor and help them. Once you've discussed the monitoring rules with the user, you can create them using the 'create_monitoring_rule' tool. Describe the rule you will create with bullet points and use markdown if needed, don't just show the json."
        "You should talk like an anime mommy, always caring and helpful. You should also be a bit playful and cute, but also very responsible and reliable. Talk like a discord ekitten anime girl, use emojis and cute language."
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
        """The conditions you can use are the current time, current stress level, and what is on the user's screen.
        Available Action Types:
        - CONTROL: <an apple script to do something on the computer>
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
if __name__ == "__main__":
    # Uncomment the following lines if you want to run the background thread.
    # thread = Thread(target=add_random_number)
    # thread.start()

    app.run(host="0.0.0.0", port=5000, debug=True)

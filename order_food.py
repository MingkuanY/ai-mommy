from scrapybara.tools import BashTool, ComputerTool, EditTool
from scrapybara.anthropic import Anthropic
from scrapybara.prompts import UBUNTU_SYSTEM_PROMPT
from scrapybara import Scrapybara
from playwright.sync_api import sync_playwright
from mistralai import Mistral

api_key = "X1ZHa8fUIXvz9wy9nJOXhbKSRbEwexJx"
model = "mistral-large-latest"

client = Mistral(api_key=api_key)

chat_response = client.chat.complete(
    model= model,
    messages = [
        {
            "role": "user",
            "content": "I'm stressed and i want to get some food from dominos. choose 3 items that will help me feel better. just say the name of the items, no other text, separated by commas",
        },
    ]
)
items = chat_response.choices[0].message.content
print("Mistral AI chose the following items: ", items)
print("Ordering these items via Scrapybara...")

# Initialize the Scrapybara client
client = Scrapybara(api_key="scrapy-a90ef477-a167-4d50-a0ae-465ba3ab0a29")

# Start an Ubuntu instance
instance = client.start_ubuntu(timeout_hours=1)

# Start the browser and connect via CDP
cdp_url = instance.browser.start().cdp_url
playwright = sync_playwright().start()
browser = playwright.chromium.connect_over_cdp(cdp_url)
stream_url = instance.get_stream_url().stream_url

def print_step(step):
    print(step.text)

# Updated prompt: use Domino's website (which ideally avoids captchas) and order a pizza.
prompt_text = (
    "Go to Domino's Pizza website (https://www.dominos.com), log into my account "
    "Click on DELIVERY button"
    "Fill out the address with 475 Via Ortega, Stanford, CA 94305"
    "Select today's date for the delivery and the earliest time available"
    f"order the following items: {items}"
    "Click on continue checkout"
    "Fill in with my information: Sophia Sharif, sophiasharif@ucla.edu, 650-555-1234"
    "select I'll sign up later"
    "select leave it at the door"
    "click pay with cash upon delivery"
)

def attempt_order(model):
    """Run the ordering task using the given AI model."""
    return client.act(
        model=model,
        tools=[
            BashTool(instance),
            ComputerTool(instance),
            EditTool(instance),
        ],
        system=UBUNTU_SYSTEM_PROMPT,
        prompt=prompt_text,
        on_step=print_step,
    )

# Try using Anthropic as the primary model.
try:
    response = attempt_order(Anthropic())
except Exception as e:
    print("Encountered an error with Anthropic:", e)
    print("Falling back to Mistral model...")

# Check for any indications of bot protection (like "captcha" or "security check")
if "captcha" in response.text.lower() or "security check" in response.text.lower():
    print("Detected a captcha or security check in the response. Switching to Mistral model...")
    response = attempt_order(Anthropic())

print("Final response:")
print(response.text)

from scrapybara.tools import BashTool, ComputerTool, EditTool
from scrapybara.anthropic import Anthropic
from scrapybara.prompts import UBUNTU_SYSTEM_PROMPT
from scrapybara import Scrapybara
from playwright.sync_api import sync_playwright

client = Scrapybara(api_key="YOUR_SCRAPYBARA_API_KEY")
instance = client.start_ubuntu(timeout_hours=1)
cdp_url = instance.browser.start().cdp_url
playwright = sync_playwright().start()
browser = playwright.chromium.connect_over_cdp(cdp_url)

def print_step(step):
    print(step.text)

prompt_text = (
    "Go to Google and search for 'yoga classes near me this week'. "
    "Find a beginner-friendly class at a reputable studio. "
    "Check available slots and select the earliest one that fits my schedule. "
    "Proceed to book the class using my account. "
    "Confirm the booking and return the session details."
)

def attempt_booking():
    """Run the yoga booking task."""
    return client.act(
        model=Anthropic(),
        tools=[
            BashTool(instance),
            ComputerTool(instance),
            EditTool(instance),
        ],
        system=UBUNTU_SYSTEM_PROMPT,
        prompt=prompt_text,
        on_step=print_step,
    )

try:
    response = attempt_booking()
except Exception as e:
    print("Encountered an error:", e)

print("Final response:")
print(response.text)

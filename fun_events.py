from scrapybara.tools import BashTool, ComputerTool, EditTool
from scrapybara.anthropic import Anthropic
from scrapybara.prompts import UBUNTU_SYSTEM_PROMPT
from scrapybara import Scrapybara
from playwright.sync_api import sync_playwright

# Initialize Scrapybara client
client = Scrapybara(api_key="YOUR_SCRAPYBARA_API_KEY")

# Start an Ubuntu instance
instance = client.start_ubuntu(timeout_hours=1)

# Start the browser
cdp_url = instance.browser.start().cdp_url
playwright = sync_playwright().start()
browser = playwright.chromium.connect_over_cdp(cdp_url)

def print_step(step):
    print(step.text)

# Event Search Prompt
prompt_text = (
    "Go to Eventbrite and search for fun local events happening this weekend. "
    "Filter events by 'highly rated' and 'outdoor' categories. "
    "Select the top three events based on popularity and return: "
    "- Event name "
    "- Location "
    "- Date & time "
    "- Ticket price "
    "- Booking link."
)

def attempt_event_search():
    """Run the local event search task."""
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
    response = attempt_event_search()
except Exception as e:
    print("Encountered an error:", e)

print("Final response:")
print(response.text)

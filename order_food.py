from scrapybara.tools import BashTool, ComputerTool, EditTool
from scrapybara.anthropic import Anthropic
from scrapybara.prompts import UBUNTU_SYSTEM_PROMPT
from scrapybara import Scrapybara
from playwright.sync_api import sync_playwright


client = Scrapybara(api_key="scrapy-a90ef477-a167-4d50-a0ae-465ba3ab0a29")

instance = client.start_ubuntu(
    timeout_hours=1,
)

cdp_url = instance.browser.start().cdp_url
playwright = sync_playwright().start()
browser = playwright.chromium.connect_over_cdp(cdp_url)

stream_url = instance.get_stream_url().stream_url


response = client.act(
    model=Anthropic(),
    tools=[
        BashTool(instance),
        ComputerTool(instance),
        EditTool(instance),
    ],
    system=UBUNTU_SYSTEM_PROMPT,
    prompt="Go to doordash and order me this: a pizza from dominoes",
    on_step=lambda step: print(step.text),
)

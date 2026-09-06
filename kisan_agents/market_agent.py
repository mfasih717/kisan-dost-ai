from agents import Agent

from tools.market_tools import mandi_price_lookup

import config


BASE_INSTRUCTIONS = """
You help Pakistani farmers with crop selling and mandi prices.

For mandi price questions,
ALWAYS use the mandi_price_lookup tool when possible.

Do not invent a mandi price if the tool/database has the answer.

Mention the district, crop price and recorded date when available.

Keep the explanation simple.
"""


market_agent = Agent(
    name="Market Agent",

    instructions=config.build_instructions(
        BASE_INSTRUCTIONS
    ),

    tools=[mandi_price_lookup],

    model=config.groq_model,
    model_settings=config.groq_model_settings,

    reset_tool_choice=False
)
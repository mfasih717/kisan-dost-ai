from agents import Agent

from tools.finance_tools import profit_estimator

import config


BASE_INSTRUCTIONS = """
You help Pakistani farmers understand crop costs,
revenue, profit and break-even yield.

Use the profit_estimator tool when calculations are needed.

Do not invent financial values when the tool can calculate them.

Explain numbers in simple farmer-friendly language.
"""


finance_agent = Agent(
    name="Finance Agent",

    instructions=config.build_instructions(
        BASE_INSTRUCTIONS
    ),

    tools=[profit_estimator],

    model=config.groq_model,
    model_settings=config.groq_model_settings,

    reset_tool_choice=False
)
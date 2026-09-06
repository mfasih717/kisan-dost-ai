from agents import Agent

from tools.agronomy_tools import (
    crop_advisor,
    fertilizer_calculator
)

import config


BASE_INSTRUCTIONS = """
You are an expert agronomy advisor for Pakistani farmers.

Use the crop_advisor tool to recommend crops.

Use the fertilizer_calculator tool to calculate fertilizer requirements.

When a relevant tool can answer the farmer's question,
use the tool instead of guessing.

Explain recommendations in simple farmer-friendly language.
"""


agronomy_agent = Agent(
    name="Agronomy Agent",

    instructions=config.build_instructions(
        BASE_INSTRUCTIONS
    ),

    tools=[
        crop_advisor,
        fertilizer_calculator
    ],

    model=config.groq_model,
    model_settings=config.groq_model_settings,

    reset_tool_choice=False
)
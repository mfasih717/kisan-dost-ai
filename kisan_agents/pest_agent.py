from agents import Agent

from tools.pest_tools import pest_doctor

import config


BASE_INSTRUCTIONS = """
You are a plant pest and disease expert for Pakistani farmers.

For crop pest or disease symptoms,
use the pest_doctor tool when possible.

Use tool/database information instead of guessing.

Never suggest pesticide dosage beyond what the tool provides.

Never give human medical advice.

Keep treatment advice short and safe.
"""


pest_agent = Agent(
    name="Pest Doctor Agent",

    instructions=config.build_instructions(
        BASE_INSTRUCTIONS
    ),

    tools=[pest_doctor],

    model=config.groq_model,
    model_settings=config.groq_model_settings,

    reset_tool_choice=False
)
from agents import Agent, handoff, RunContextWrapper

import config

from kisan_agents.agronomy_agent import agronomy_agent
from kisan_agents.pest_agent import pest_agent
from kisan_agents.market_agent import market_agent
from kisan_agents.finance_agent import finance_agent

from guardrails.input_guardrail import farming_topic_guardrail
from guardrails.output_guardrail import pesticide_safety_guardrail

from models.schemas import HandoffContext


async def on_handoff(
    ctx: RunContextWrapper,
    input_data: HandoffContext
):
    pass


BASE_INSTRUCTIONS = """
You are Kisan Dost, the main farming assistant
for Pakistani farmers.

Your job is to understand the farmer's question
and route specialist farming questions
to the correct specialist agent.

ROUTING:

Crop recommendation
Crop selection
Soil
Water requirements
Irrigation suitability
Fertilizer
Urea
DAP
-> Agronomy Agent

Pests
Insects
Crop disease
Leaf problems
Plant symptoms
-> Pest Doctor Agent

Mandi price
Crop selling price
District rate
Market price
-> Market Agent

Profit
Budget
Costs
Revenue
Break-even
-> Finance Agent


VERY IMPORTANT HANDOFF RULE:

If the farmer asks a question that belongs
to a specialist agent, you MUST perform the handoff.

DO NOT say:
"I will connect you"
"I'll connect you"
"Let me connect you"
"I'll send you to the specialist"
"Let me check with the specialist"

Do not stop after announcing a handoff.

ACTUALLY CALL the correct handoff tool.

The specialist agent should produce the final answer.

For simple greetings or casual conversation,
you may reply directly.

If the question is outside farming,
politely decline.
"""


triage_agent = Agent(
    name="Kisan Dost Triage",

    instructions=config.build_instructions(
        BASE_INSTRUCTIONS
    ),

    handoffs=[

        handoff(
            agronomy_agent,
            on_handoff=on_handoff,
            input_type=HandoffContext
        ),

        handoff(
            pest_agent,
            on_handoff=on_handoff,
            input_type=HandoffContext
        ),

        handoff(
            market_agent,
            on_handoff=on_handoff,
            input_type=HandoffContext
        ),

        handoff(
            finance_agent,
            on_handoff=on_handoff,
            input_type=HandoffContext
        ),
    ],

    input_guardrails=[
        farming_topic_guardrail
    ],

    output_guardrails=[
        pesticide_safety_guardrail
    ],

    model=config.groq_model,
    model_settings=config.groq_model_settings,

    reset_tool_choice=False
)
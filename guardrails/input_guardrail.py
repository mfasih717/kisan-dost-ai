from agents import (
    input_guardrail,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Agent,
)


FARMING_KEYWORDS = [
    "farm", "farming", "agriculture", "crop", "crops",
    "wheat", "cotton", "rice", "maize", "sugarcane",
    "fertilizer", "urea", "dap",
    "pest", "insect", "disease",
    "irrigation", "water", "soil",
    "mandi", "price", "rate",
    "profit", "budget", "yield",
    "kheti", "fasal", "zameen"
]

CASUAL_KEYWORDS = [
    "hi", "hello", "hey", "salam", "assalam",
    "my name is", "mera naam", "thanks", "thank you",
    "how are you", "kaise ho", "kese ho",
    "good morning", "good evening", "good night"
]


@input_guardrail
async def farming_topic_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    input_text: str
) -> GuardrailFunctionOutput:

    text = str(input_text).lower().strip()

    is_farming_related = any(
        keyword in text
        for keyword in FARMING_KEYWORDS
    )

    is_casual_talk = any(
        keyword in text
        for keyword in CASUAL_KEYWORDS
    )

    allowed = is_farming_related or is_casual_talk

    return GuardrailFunctionOutput(
        output_info={
            "is_farming_related": is_farming_related,
            "is_casual_talk": is_casual_talk
        },
        tripwire_triggered=not allowed,
    )
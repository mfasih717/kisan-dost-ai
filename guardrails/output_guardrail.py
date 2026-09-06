from agents import (
    output_guardrail,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Agent,
)

UNSAFE_KEYWORDS = ["human dose", "for humans", "drink this", "human consumption", "eat the pesticide"]


@output_guardrail
async def pesticide_safety_guardrail(
    ctx: RunContextWrapper, agent: Agent, output
) -> GuardrailFunctionOutput:
    output_text = str(output).lower()
    is_unsafe = any(keyword in output_text for keyword in UNSAFE_KEYWORDS)

    return GuardrailFunctionOutput(
        output_info={"checked": True, "flagged_unsafe": is_unsafe},
        tripwire_triggered=is_unsafe,
    )
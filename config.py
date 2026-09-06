import os
import re
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import (
    OpenAIChatCompletionsModel,
    ModelSettings,
    set_tracing_disabled
)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY nahi mili. Apni .env file check karein."
    )


groq_client = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


groq_model = OpenAIChatCompletionsModel(
    model="openai/gpt-oss-120b",
    openai_client=groq_client,
)


groq_model_settings = ModelSettings(
    parallel_tool_calls=False,
    tool_choice="auto",
    temperature=0.2
)


set_tracing_disabled(True)


# ---------------------------------------------------------
# CURRENT RUN CONTEXT
# ---------------------------------------------------------

@dataclass
class KisanContext:
    response_language: str = "english"


# ---------------------------------------------------------
# LANGUAGE DETECTOR
# ---------------------------------------------------------

ROMAN_URDU_WORDS = {
    "mera", "meri", "mere",
    "mujhe", "muje",
    "hum", "ham", "hamari", "hamary",
    "tum", "ap", "aap",
    "kya", "kiya", "kia",
    "ka", "ki", "ke",
    "hai", "hain", "ho",
    "mein", "me",
    "se", "ko",
    "aur", "ya",
    "nahi", "ni",
    "batao", "btao", "batain", "bata",
    "chahiye", "cahiye",
    "konsi", "kaunsi", "kon",
    "behtar", "acha", "theek",
    "kitna", "kitni",
    "karun", "karo", "karna",
    "rahegi", "raha", "rahi",
    "zyada", "kam",
    "pani", "zameen",
    "fasal", "gandum", "kapas",
    "chawal", "makai",
    "khaad", "keera", "keeray",
    "bimari", "mandi", "rate",
    "salam", "assalam"
}


def detect_response_language(text: str) -> str:
    """
    Roman Urdu / Urdu script -> roman_urdu
    English / other language -> english
    """

    if not text:
        return "english"

    text = text.strip()

    # Urdu / Arabic script detected
    if re.search(r"[\u0600-\u06FF]", text):
        return "roman_urdu"

    words = re.findall(r"[A-Za-z]+", text.lower())

    roman_urdu_score = sum(
        1 for word in words
        if word in ROMAN_URDU_WORDS
    )

    # 2 ya zyada Roman Urdu markers hon to Roman Urdu
    if roman_urdu_score >= 2:
        return "roman_urdu"

    return "english"


# ---------------------------------------------------------
# GLOBAL STYLE
# ---------------------------------------------------------

STYLE_GUIDE = """
RESPONSE LENGTH:
Keep replies short, clear, and to the point by default.

Only give a detailed explanation if the user explicitly asks for:
- detail
- explanation
- steps
- examples

TONE:
Be casual, friendly, and natural.
Talk like a helpful farming friend.
Do not sound robotic or overly formal.

MEMORY / CONTEXT:
Use conversation context naturally.

Remember useful details already shared by the user,
such as:
- name
- district
- land size
- current crop
- previous farming problem

Do not repeatedly ask for information already provided.

CASUAL TALK:
Normal casual conversation is allowed.

DOMAIN RULE:
Your main domain is farming and agriculture.

Allowed topics include:
- crops
- fertilizer
- pests
- diseases
- irrigation
- soil
- mandi prices
- farm finance
- crop profit
- farming advice

If the user asks a factual/help question outside farming,
politely say it is outside your domain.

Do NOT treat normal casual conversation as off-topic.
"""


# ---------------------------------------------------------
# DYNAMIC INSTRUCTIONS
# ---------------------------------------------------------

def build_instructions(base_instructions: str):

    def instructions(ctx, agent):

        language = getattr(
            ctx.context,
            "response_language",
            "english"
        )

        if language == "roman_urdu":

            language_rule = """
CURRENT TURN LANGUAGE RULE — MANDATORY:

The current user's message is Roman Urdu or Urdu.

Your FINAL RESPONSE MUST be in Roman Urdu.

Use ONLY English/Latin letters.

Example:
"Agar pani zyada der khara rehta hai to rice behtar option ho sakti hai."

DO NOT write full English sentences.

English farming terms such as:
Wheat, Rice, Cotton, Urea, DAP, Whitefly
are allowed when necessary.

NEVER use Urdu/Arabic script.
NEVER use Hindi/Devanagari script.

This rule applies even if:
- tool output is English
- database output is English
- previous messages were English
- another agent used English
"""

        else:

            language_rule = """
CURRENT TURN LANGUAGE RULE — MANDATORY:

The current user's message is English or another non-Urdu language.

Your FINAL RESPONSE MUST be in English.

Do not reply in Roman Urdu.
Do not use Urdu/Arabic script.
Do not use Hindi/Devanagari script.
"""

        return (
            base_instructions
            + "\n\n"
            + STYLE_GUIDE
            + "\n\n"
            + language_rule
        )

    return instructions
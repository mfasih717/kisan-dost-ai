import os
import uuid
import asyncio

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session as flask_session
)

from agents import Runner, SQLiteSession

from agents.exceptions import (
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
)

import config

from kisan_agents.triage_agent import triage_agent
from kisan_agents.agronomy_agent import agronomy_agent
from kisan_agents.pest_agent import pest_agent
from kisan_agents.market_agent import market_agent
from kisan_agents.finance_agent import finance_agent


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

# "hackathon" ka word remove kar diya hai
app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "kisan-dost-secret-key"
)


# =========================================================
# BROWSER USER ID
# =========================================================

def get_browser_user_id():
    """
    Har browser/user ko unique ID deta hai.
    """

    if "farmer_session_id" not in flask_session:
        flask_session["farmer_session_id"] = uuid.uuid4().hex

    return flask_session["farmer_session_id"]


# =========================================================
# SEPARATE SESSION FOR EACH AGENT
# =========================================================

def get_agent_session(agent_key: str):
    """
    Har specialist agent ki alag conversation history hoti hai.

    Is se Triage ke purane handoff tool calls
    Agronomy/Pest/Market/Finance ko disturb nahi karte.
    """

    browser_id = get_browser_user_id()

    session_id = (
        f"farmer_web_v3_{browser_id}_{agent_key}"
    )

    return SQLiteSession(
        session_id,
        "database/kisan_dost.db"
    )


# =========================================================
# AGENT KEY -> AGENT OBJECT
# =========================================================

def get_agent_by_key(agent_key: str):

    agents_map = {
        "agronomy": agronomy_agent,
        "pest": pest_agent,
        "market": market_agent,
        "finance": finance_agent,
        "triage": triage_agent
    }

    return agents_map.get(
        agent_key,
        triage_agent
    )


# =========================================================
# AGENT DISPLAY NAME
# =========================================================

def get_agent_name(agent_key: str):

    names = {
        "agronomy": "Agronomy Agent",
        "pest": "Pest Doctor Agent",
        "market": "Market Agent",
        "finance": "Finance Agent",
        "triage": "Kisan Dost"
    }

    return names.get(
        agent_key,
        "Kisan Dost"
    )


# =========================================================
# SHORT FOLLOW-UP CHECK
# =========================================================

def is_short_followup(message: str):
    """
    Example:
    RABI
    loamy
    Faisalabad
    8 acre
    yes
    no

    Aise short answers ko previous specialist
    ke paas wapas bhejna hai.
    """

    words = message.strip().split()

    return len(words) <= 4


# =========================================================
# PYTHON ROUTER
# =========================================================

def select_agent(user_message: str):
    """
    User ke sawal ko correct specialist agent tak bhejta hai.
    """

    text = user_message.lower().strip()


    # -----------------------------------------------------
    # PEST / DISEASE
    # -----------------------------------------------------

    pest_keywords = [
        "pest",
        "disease",
        "insect",
        "insects",
        "whitefly",
        "armyworm",
        "rust",
        "fungus",
        "spots",
        "yellow leaves",
        "leaf curling",
        "leaves curling",
        "keera",
        "keeray",
        "keere",
        "keery",
        "kira",
        "bimari",
        "bemaari",
        "pattay peelay",
        "patte peele",
        "curl",
        "sundhi",
        "sundi",
        "makhi"
    ]

    if any(keyword in text for keyword in pest_keywords):

        return (
            pest_agent,
            "pest",
            "Pest Doctor Agent"
        )


    # -----------------------------------------------------
    # MARKET / MANDI
    # -----------------------------------------------------

    market_keywords = [
        "mandi",
        "market price",
        "market rate",
        "selling price",
        "sell",
        "price",
        "rate",
        "rates",
        "maund",
        "per maund",
        "bhav",
        "qeemat",
        "keemat"
    ]

    if any(keyword in text for keyword in market_keywords):

        return (
            market_agent,
            "market",
            "Market Agent"
        )


    # -----------------------------------------------------
    # FINANCE / PROFIT
    # -----------------------------------------------------

    finance_keywords = [
        "profit",
        "budget",
        "cost",
        "costs",
        "expense",
        "expenses",
        "revenue",
        "income",
        "margin",
        "break even",
        "break-even",
        "munafa",
        "faida",
        "kharcha",
        "kamai",
        "earning"
    ]

    if any(keyword in text for keyword in finance_keywords):

        return (
            finance_agent,
            "finance",
            "Finance Agent"
        )


    # -----------------------------------------------------
    # AGRONOMY
    # -----------------------------------------------------

    agronomy_keywords = [
        "crop",
        "crops",
        "fasal",
        "faslain",

        "wheat",
        "gandum",

        "cotton",
        "kapas",

        "rice",
        "chawal",

        "maize",
        "makai",

        "sugarcane",
        "ganna",

        "chickpea",
        "chana",

        "fertilizer",
        "urea",
        "dap",
        "khaad",
        "khad",

        "soil",
        "zameen",
        "land",

        "water",
        "pani",
        "irrigation",

        "acre",
        "acres",
        "yield",

        "rabi",
        "kharif",
        "sardi",
        "garmi",

        "loamy",
        "sandy",
        "clay",
        "mitti",
        "soil type",

        "behtar rahegi",
        "behtar hai",
        "konsi fasal",
        "kaunsi fasal",

        "lagao",
        "lagaon",
        "ugao",
        "boai"
    ]

    if any(keyword in text for keyword in agronomy_keywords):

        return (
            agronomy_agent,
            "agronomy",
            "Agronomy Agent"
        )


    # -----------------------------------------------------
    # SHORT FOLLOW-UP
    # -----------------------------------------------------

    if is_short_followup(user_message):

        previous_agent_key = flask_session.get(
            "last_agent_key"
        )

        if previous_agent_key:

            previous_agent = get_agent_by_key(
                previous_agent_key
            )

            return (
                previous_agent,
                previous_agent_key,
                get_agent_name(previous_agent_key)
            )


    # -----------------------------------------------------
    # DEFAULT -> TRIAGE
    # -----------------------------------------------------

    return (
        triage_agent,
        "triage",
        "Kisan Dost"
    )


# =========================================================
# CLEAN RESPONSE
# =========================================================

def clean_reply(final_output):
    """
    Agent response ko clean text mein convert karta hai
    aur duplicate reply remove karta hai.
    """

    if final_output is None:
        return "Mujhe response nahi mila."


    # -----------------------------------------------------
    # NORMAL STRING
    # -----------------------------------------------------

    if isinstance(final_output, str):

        reply = final_output


    # -----------------------------------------------------
    # STRUCTURED / PYDANTIC OUTPUT
    # -----------------------------------------------------

    elif hasattr(final_output, "model_dump"):

        data = final_output.model_dump()

        reply = None

        possible_keys = (
            "reply",
            "response",
            "answer",
            "message",
            "text",
            "output",
            "replies",
        )

        for key in possible_keys:

            value = data.get(key)

            if value:

                if isinstance(value, list):

                    reply = "\n".join(
                        str(item)
                        for item in value
                    )

                else:

                    reply = str(value)

                break


        if reply is None:
            reply = str(final_output)


    else:

        reply = str(final_output)


    reply = reply.strip()


    # -----------------------------------------------------
    # DUPLICATE MARKERS
    # -----------------------------------------------------

    duplicate_markers = [
        " replies.",
        " reply.",
        " response.",
        " responses.",
    ]

    lower_reply = reply.lower()


    for marker in duplicate_markers:

        marker_index = lower_reply.find(marker)

        if marker_index != -1:

            left = reply[:marker_index].strip()

            right = reply[
                marker_index + len(marker):
            ].strip()


            if (
                left
                and right
                and left.lower() == right.lower()
            ):

                return left


    # -----------------------------------------------------
    # EXACT HALF DUPLICATE
    # -----------------------------------------------------

    length = len(reply)

    if length % 2 == 0:

        half = length // 2

        first_half = reply[:half].strip()

        second_half = reply[half:].strip()


        if (
            first_half.lower()
            == second_half.lower()
        ):

            return first_half


    return reply


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# CHAT API
# =========================================================

@app.route(
    "/chat",
    methods=["POST"]
)
def chat():

    user_message = ""

    response_language = "english"


    try:

        # =================================================
        # GET MESSAGE
        # =================================================

        data = (
            request.get_json(
                silent=True
            )
            or {}
        )


        user_message = str(
            data.get("message")
            or ""
        ).strip()


        if not user_message:

            return jsonify({
                "error": "Message required"
            }), 400


        # =================================================
        # LANGUAGE DETECTION
        # =================================================

        detected_language = (
            config.detect_response_language(
                user_message
            )
        )


        # -------------------------------------------------
        # SHORT FOLLOW-UP KI LANGUAGE
        # -------------------------------------------------

        if is_short_followup(user_message):

            response_language = flask_session.get(
                "last_response_language",
                detected_language
            )

        else:

            response_language = detected_language


        # Current language save karo
        flask_session[
            "last_response_language"
        ] = response_language


        print(
            f"[LANGUAGE] {response_language}"
        )


        # =================================================
        # RUN CONTEXT
        # =================================================

        kisan_context = config.KisanContext(
            response_language=response_language
        )


        # =================================================
        # SELECT AGENT
        # =================================================

        selected_agent, agent_key, agent_name = (
            select_agent(
                user_message
            )
        )


        # -------------------------------------------------
        # PREVIOUS AGENT YAAD RAKHO
        # -------------------------------------------------

        flask_session[
            "last_agent_key"
        ] = agent_key


        print(
            f"[ROUTER] Selected: {agent_name}"
        )


        # =================================================
        # GET CORRECT AGENT SESSION
        # =================================================

        agent_session = get_agent_session(
            agent_key
        )


        # =================================================
        # RUN AGENT
        # =================================================

        result = asyncio.run(

            Runner.run(
                selected_agent,
                user_message,

                context=kisan_context,

                session=agent_session
            )

        )


        # =================================================
        # CLEAN RESPONSE
        # =================================================

        reply = clean_reply(
            result.final_output
        )


        print(
            f"[RESPONSE] {reply}"
        )


        return jsonify({
            "reply": reply
        }), 200


    # =====================================================
    # OFF-TOPIC
    # =====================================================

    except InputGuardrailTripwireTriggered:

        print(
            "[GUARDRAIL] Off-topic input blocked."
        )


        if response_language == "roman_urdu":

            reply = (
                "Ye sawal meri farming domain se bahar hai yaar. "
                "Fasal, fertilizer, pests, mandi, irrigation "
                "ya farm profit ke bare mein pooch lo."
            )

        else:

            reply = (
                "That question is outside my farming domain. "
                "You can ask me about crops, fertilizer, pests, "
                "irrigation, mandi prices or farm profit."
            )


        return jsonify({
            "reply": reply
        }), 200


    # =====================================================
    # SAFETY
    # =====================================================

    except OutputGuardrailTripwireTriggered:

        print(
            "[GUARDRAIL] Unsafe output blocked."
        )


        if response_language == "roman_urdu":

            reply = (
                "Is jawab mein safety concern tha, "
                "is liye main wo advice share nahi kar sakta."
            )

        else:

            reply = (
                "That response had a safety concern, "
                "so I cannot share that advice."
            )


        return jsonify({
            "reply": reply
        }), 200


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as e:

        print("\n" + "=" * 70)
        print("[WEB ERROR]")
        print("Error Type:", type(e).__name__)
        print("Error:", str(e))
        print("=" * 70 + "\n")


        if response_language == "roman_urdu":

            message = (
                "Kuch masla ho gaya. "
                "Backend error terminal mein print ho gaya hai."
            )

        else:

            message = (
                "Something went wrong. "
                "The backend error has been printed in the terminal."
            )


        return jsonify({
            "error": message
        }), 500


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )
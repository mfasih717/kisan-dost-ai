import asyncio
from agents import Runner, SQLiteSession
from agents.exceptions import InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered
import config
from kisan_agents.triage_agent import triage_agent


async def main():
    print("=" * 50)
    print("🌾 Kisan Dost - Aapka Zarai Madadgar")
    print("=" * 50)
    print("Apna sawal likhein (ya 'exit' likh kar band karein)\n")

    session = SQLiteSession("farmer_session_1", "database/kisan_dost.db")

    while True:
        user_input = input("Farmer: ")
        if user_input.strip().lower() in ["exit", "quit", "bye"]:
            print("Allah Hafiz! Kisan Dost hamesha aapke saath hai.")
            break

        try:
            result = await Runner.run(triage_agent, user_input, session=session)
            print(f"\nKisan Dost: {result.final_output}\n")
        except InputGuardrailTripwireTriggered:
            print("\nKisan Dost: Sorry yaar, meri domain sirf kheti-baari hai — is sawal me madad nahi kar sakta.\n")
        except OutputGuardrailTripwireTriggered:
            print("\nKisan Dost: Ye jawab safe nahi tha, dobara poocho please.\n")
        except Exception:
            print("\n[Retry ho raha hai...]")
            try:
                result = await Runner.run(triage_agent, user_input, session=session)
                print(f"\nKisan Dost: {result.final_output}\n")
            except Exception as e2:
                print(f"\n[Error] Kuch masla ho gaya: {e2}\n")


if __name__ == "__main__":
    asyncio.run(main())
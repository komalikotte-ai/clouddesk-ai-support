from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.append(
    str(PROJECT_ROOT)
)


from backend.support_agent import SupportAgent


agent = SupportAgent()


questions = [
    "Why was I charged twice?",
    "I forgot my password",
    "The dashboard is very slow",
    "Can you help me book a flight?"
]


for question in questions:

    print("\n")
    print("=" * 70)

    print(
        "CUSTOMER:",
        question
    )

    print("=" * 70)

    result = agent.process_message(
        question
    )

    print(
        "\nCATEGORY:",
        result["category"]
    )

    print(
        "CONFIDENCE:",
        result["confidence"]
    )

    print(
        "STATUS:",
        result["status"]
    )

    print(
        "REASON:",
        result["reason"]
    )

    print(
        "\nANSWER:"
    )

    print(
        result["answer"]
    )

    print(
        "\nSOURCES:"
    )

    for source in result["sources"]:

        print(
            f"- {source['source']} "
            f"(distance: {source['distance']:.3f})"
        )
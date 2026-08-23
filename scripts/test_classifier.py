from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.append(
    str(PROJECT_ROOT)
)


from backend.classifier import TicketClassifier


classifier = TicketClassifier()


messages = [
    "Why was I charged twice?",
    "I forgot my password",
    "The dashboard is very slow",
    "How can I download my invoice?",
    "My account is locked",
    "Can you help me book a flight?"
]


for message in messages:

    result = classifier.classify(
        message
    )

    print("\n" + "=" * 60)

    print(
        "MESSAGE:",
        message
    )

    print(
        "CATEGORY:",
        result["category"]
    )

    print(
        "CONFIDENCE:",
        result["confidence"]
    )

    print(
        "REASON:",
        result["reason"]
    )

    print(
        "SCORES:",
        result["scores"]
    )
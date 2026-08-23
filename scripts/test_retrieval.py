from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.append(
    str(PROJECT_ROOT)
)


from backend.rag import RAGEngine


rag = RAGEngine()


questions = [
    "I forgot my password",
    "Why was I charged twice?",
    "The dashboard is very slow"
]


for question in questions:

    print("\n" + "=" * 60)
    print("QUESTION:", question)
    print("=" * 60)

    results = rag.search(
        question,
        top_k=2
    )

    for index, result in enumerate(results, start=1):

        print(f"\nRESULT {index}")
        print("SOURCE:", result["metadata"]["source"])
        print("DISTANCE:", result["distance"])
        print("CONTENT:")
        print(result["document"])
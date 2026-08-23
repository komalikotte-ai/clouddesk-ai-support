from pathlib import Path
import sys


# Allow Python to find the backend package
PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.append(
    str(PROJECT_ROOT)
)


from backend.rag import RAGEngine


KNOWLEDGE_BASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "knowledge_base"
)


def load_documents():

    documents = []
    ids = []
    metadatas = []

    for file_path in KNOWLEDGE_BASE_PATH.glob("*.txt"):

        text = file_path.read_text(
            encoding="utf-8"
        )

        # Separate individual FAQ entries.
        chunks = [
            chunk.strip()
            for chunk in text.split("\n\n")
            if chunk.strip()
        ]

        # Skip the document title.
        for index, chunk in enumerate(chunks):

            if index == 0:
                continue

            documents.append(chunk)

            ids.append(
                f"{file_path.stem}_{index}"
            )

            metadatas.append(
                {
                    "source": file_path.name
                }
            )

    return documents, ids, metadatas


if __name__ == "__main__":

    print("Reading knowledge base...")

    documents, ids, metadatas = load_documents()

    print(
        f"Found {len(documents)} FAQ entries."
    )

    rag = RAGEngine()

    rag.add_documents(
        documents,
        ids,
        metadatas
    )

    print(
        f"Successfully indexed "
        f"{len(documents)} FAQ entries."
    )
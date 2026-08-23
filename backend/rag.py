import chromadb
from sentence_transformers import SentenceTransformer


class RAGEngine:

    # Cosine distance ranges from 0 (identical) to 2 (opposite).
    # Anything above this is treated as "not actually relevant"
    # and is dropped before it ever reaches the LLM.
    MAX_RELEVANT_DISTANCE = 0.45

    def __init__(self):

        print("Loading embedding model...")

        self.embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        self.client = chromadb.PersistentClient(
            path="./chroma_db"
        )

        # IMPORTANT: explicitly request cosine distance.
        # Chroma's default space is raw L2, whose scale depends
        # on embedding magnitude and isn't meaningfully bounded,
        # which made it impossible to set a sane relevance cutoff.
        # Cosine distance is bounded (0-2), so MAX_RELEVANT_DISTANCE
        # above is actually meaningful.
        self.collection = self.client.get_or_create_collection(
            name="clouddesk_knowledge",
            metadata={"hnsw:space": "cosine"}
        )

    # ------------------------------------------------------------
    # ADD / UPDATE DOCUMENTS
    # ------------------------------------------------------------

    def add_documents(self, documents, ids, metadatas):

        embeddings = self.embedding_model.encode(
            documents
        ).tolist()

        self.collection.upsert(
            documents=documents,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )

    # ------------------------------------------------------------
    # SEARCH KNOWLEDGE BASE
    # ------------------------------------------------------------

    def search(self, query, top_k=3, max_distance=None):

        if max_distance is None:
            max_distance = self.MAX_RELEVANT_DISTANCE

        query_embedding = self.embedding_model.encode(
            [query]
        ).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )

        documents = results.get(
            "documents",
            [[]]
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]]
        )[0]

        distances = results.get(
            "distances",
            [[]]
        )[0]

        formatted_results = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances
        ):

            # ------------------------------------------------
            # RELEVANCE CUTOFF
            # Chroma always returns your top_k nearest vectors,
            # even if none of them are actually relevant to the
            # query. Without this check, an unrelated document
            # still gets treated as valid "context" and handed
            # to the LLM, which is how irrelevant / hallucinated
            # answers sneak past the classifier stage.
            # ------------------------------------------------

            if distance is not None and distance > max_distance:
                continue

            metadata = metadata or {}

            # Try common metadata names
            source = (
                metadata.get("source")
                or metadata.get("title")
                or metadata.get("name")
                or "CloudDesk Knowledge Base"
            )

            formatted_results.append(
                {
                    # SupportAgent expects these names
                    "content": document,
                    "source": source,
                    "distance": distance,

                    # Keep original information too
                    "document": document,
                    "metadata": metadata
                }
            )

        return formatted_results

"""
Diagnostic: shows the raw distance values ChromaDB returns for a
query, with NO relevance cutoff applied, so we can see what the
real numbers look like and tune MAX_RELEVANT_DISTANCE correctly
instead of guessing.

Run from the project root:
    python debug_rag.py
"""

from backend.rag import RAGEngine

QUESTION = "How do I reset my password?"

rag = RAGEngine()

# Report what distance space the collection is actually using.
try:
    meta = rag.collection.metadata
    print(f"Collection metadata: {meta}")
except Exception as e:
    print(f"Could not read collection metadata: {e}")

print(f"\nQuery: {QUESTION!r}")
print(f"Current cutoff (rag.MAX_RELEVANT_DISTANCE): {rag.MAX_RELEVANT_DISTANCE}\n")

# max_distance=999 disables the cutoff so we see everything Chroma
# actually finds, regardless of how "far" it thinks it is.
results = rag.search(QUESTION, top_k=5, max_distance=999)

if not results:
    print("No results at all -- the collection may be empty. "
          "Did your ingestion script actually run successfully?")
else:
    for i, r in enumerate(results, start=1):
        print(f"--- result {i} ---")
        print(f"distance: {r['distance']}")
        print(f"source:   {r['source']}")
        print(f"content:  {r['content'][:200]}")
        print()

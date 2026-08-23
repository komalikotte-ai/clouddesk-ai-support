from backend.classifier import TicketClassifier
from backend.rag import RAGEngine
from backend.llm import LLMService, NOT_FOUND_TOKEN


class SupportAgent:

    def __init__(self):

        print("Initializing Support AI Employee...")

        # ------------------------------------------------------------
        # 1. Ticket Classifier
        # ------------------------------------------------------------

        self.classifier = TicketClassifier()

        # ------------------------------------------------------------
        # 2. RAG Knowledge Base
        # ------------------------------------------------------------

        self.rag = RAGEngine()

        # ------------------------------------------------------------
        # 3. LLM
        # ------------------------------------------------------------

        self.llm = LLMService()

        print("Support AI Employee ready.")

    # ================================================================
    # PROCESS CUSTOMER MESSAGE
    # ================================================================

    def process_message(self, message: str):

        # ------------------------------------------------------------
        # STEP 1: CLASSIFY
        # ------------------------------------------------------------

        classification = self.classifier.classify(
            message
        )

        category = classification["category"]
        confidence = classification["confidence"]

        CONFIDENCE_THRESHOLD = 0.70

        # ------------------------------------------------------------
        # STEP 2: UNKNOWN / LOW CONFIDENCE
        # ------------------------------------------------------------

        if (
            category == "unknown"
            or confidence < CONFIDENCE_THRESHOLD
        ):

            if category == "unknown":

                reason = classification["reason"]

            else:

                reason = (
                    f"Classification confidence "
                    f"({confidence:.2f}) is below the "
                    f"required threshold "
                    f"({CONFIDENCE_THRESHOLD:.2f})."
                )

            return {
                "message": message,
                "category": category,
                "confidence": confidence,
                "status": "escalated",
                "reason": reason,
                "answer": (
                    "I'm unable to answer this confidently "
                    "using the CloudDesk support knowledge base. "
                    "I recommend escalating this request to a "
                    "human support agent."
                ),
                "sources": []
            }

        # ------------------------------------------------------------
        # STEP 3: SEARCH KNOWLEDGE BASE
        # (RAGEngine now drops results below a relevance cutoff,
        # so `results` only ever contains genuinely relevant hits.)
        # ------------------------------------------------------------

        try:

            results = self.rag.search(
                message,
                top_k=3
            )

        except Exception as e:

            print(
                f"RAG search error: {e}"
            )

            return {
                "message": message,
                "category": category,
                "confidence": confidence,
                "status": "error",
                "reason": "Knowledge base search failed.",
                "answer": (
                    "Something went wrong while searching "
                    "the CloudDesk support knowledge base. "
                    "Please try again."
                ),
                "sources": []
            }

        # ------------------------------------------------------------
        # STEP 4: NO RESULTS
        # ------------------------------------------------------------

        if not results:

            return {
                "message": message,
                "category": category,
                "confidence": confidence,
                "status": "escalated",
                "reason": (
                    "No relevant information was found in "
                    "the CloudDesk support knowledge base."
                ),
                "answer": (
                    "I couldn't find enough relevant information "
                    "in the CloudDesk support knowledge base to "
                    "answer this confidently. I recommend "
                    "escalating this request to a human support agent."
                ),
                "sources": []
            }

        # ------------------------------------------------------------
        # STEP 5: BUILD RAG CONTEXT
        # ------------------------------------------------------------

        context_parts = []

        valid_results = []

        for result in results:

            content = result.get(
                "content",
                ""
            )

            source = result.get(
                "source",
                "CloudDesk Knowledge Base"
            )

            if not content:
                continue

            valid_results.append(result)

            context_parts.append(
                f"Source: {source}\n"
                f"Content:\n{content}"
            )

        # ------------------------------------------------------------
        # STEP 6: NO VALID CONTENT
        # ------------------------------------------------------------

        if not context_parts:

            return {
                "message": message,
                "category": category,
                "confidence": confidence,
                "status": "escalated",
                "reason": (
                    "No usable information was found in "
                    "the CloudDesk support knowledge base."
                ),
                "answer": (
                    "I couldn't find enough relevant information "
                    "in the CloudDesk support knowledge base to "
                    "answer this confidently. I recommend "
                    "escalating this request to a human support agent."
                ),
                "sources": []
            }

        context = "\n\n---\n\n".join(
            context_parts
        )

        # ------------------------------------------------------------
        # STEP 7: GENERATE ANSWER
        # ------------------------------------------------------------

        try:

            answer = self.llm.generate_answer(
                message,
                context
            )

        except Exception as e:

            print(
                f"LLM error: {e}"
            )

            return {
                "message": message,
                "category": category,
                "confidence": confidence,
                "status": "error",
                "reason": "AI response generation failed.",
                "answer": (
                    "Something went wrong while processing "
                    "your request. Please try again."
                ),
                "sources": []
            }

        # ------------------------------------------------------------
        # STEP 8: DETECT LLM "NOT FOUND" RESPONSE
        # ------------------------------------------------------------
        # IMPORTANT: this used to check whether `answer` contained
        # any of a hardcoded list of refusal phrases (e.g.
        # "cannot answer", "not enough information"). That's the
        # bug that let refusals slip through as "answered": if the
        # LLM phrased its refusal in any way not in that list, the
        # check silently failed and the answer was marked grounded.
        #
        # Instead, the prompt in llm.py now requires the model to
        # return an exact sentinel token when it can't answer, and
        # we check for that token specifically. This is deterministic
        # regardless of how the LLM phrases anything else.
        # ------------------------------------------------------------

        llm_could_not_answer = (
            NOT_FOUND_TOKEN in answer
        )

        if llm_could_not_answer:

            return {
                "message": message,
                "category": category,
                "confidence": confidence,
                "status": "escalated",
                "reason": (
                    "The knowledge base did not provide "
                    "enough information to answer confidently."
                ),
                "answer": (
                    "I cannot answer this confidently using the "
                    "CloudDesk support knowledge base. I recommend "
                    "escalating this request to a human support agent."
                ),
                "sources": []
            }

        # ------------------------------------------------------------
        # STEP 9: PREPARE SOURCES
        # (only reached for a genuinely grounded, answered response)
        # ------------------------------------------------------------

        sources = []

        for result in valid_results:

            source_name = result.get(
                "source",
                "CloudDesk Knowledge Base"
            )

            if not source_name:
                continue

            sources.append(
                {
                    "source": source_name,
                    "distance": result.get(
                        "distance",
                        None
                    )
                }
            )

        # ------------------------------------------------------------
        # STEP 10: SUCCESSFUL GROUNDED ANSWER
        # ------------------------------------------------------------

        return {
            "message": message,
            "category": category,
            "confidence": confidence,
            "status": "answered",
            "reason": classification["reason"],
            "answer": answer,
            "sources": sources
        }

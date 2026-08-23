class TicketClassifier:

    def __init__(self):

        self.categories = {
            "billing": [
                "bill",
                "billing",
                "charged",
                "charge",
                "payment",
                "invoice",
                "refund",
                "subscription",
                "price",
                "plan"
            ],

            "technical": [
                "slow",
                "loading",
                "error",
                "bug",
                "crash",
                "dashboard",
                "browser",
                "website",
                "export",
                "technical",
                "not working",
                "unavailable"
            ],

            "account_access": [
                "password",
                "login",
                "log in",
                "locked",
                "account",
                "email",
                "two factor",
                "two factor",
                "2fa",
                "verification",
                "access"
            ]
        }

    def classify(self, message):

        message = message.lower()

        scores = {
            category: 0
            for category in self.categories
        }

        for category, keywords in self.categories.items():

            for keyword in keywords:

                if keyword in message:
                    scores[category] += 1

        best_category = max(
            scores,
            key=scores.get
        )

        best_score = scores[best_category]

        # No matching category
        if best_score == 0:

            return {
                "category": "unknown",
                "confidence": 0.0,
                "reason": "No supported category matched the message.",
                "scores": scores
            }

        # More than one category has similar evidence
        sorted_scores = sorted(
            scores.values(),
            reverse=True
        )

        if (
            len(sorted_scores) > 1
            and sorted_scores[0] == sorted_scores[1]
        ):

            return {
                "category": "unknown",
                "confidence": 0.3,
                "reason": "The message matches multiple categories with similar confidence.",
                "scores": scores
            }

        # Simple transparent confidence calculation.
        # NOTE: this is keyword-count based, not a measure of
        # whether the knowledge base actually covers the topic.
        # A single keyword match (e.g. "password") reaches 0.70
        # on its own, which is enough to clear the classifier
        # stage even for topics the knowledge base has no real
        # content for. That's expected and fine as long as the
        # downstream RAG relevance cutoff and the LLM's NOT_FOUND
        # sentinel are the ones that make the final "can we
        # actually answer this" call -- the classifier is only
        # meant to route the ticket to a category, not to decide
        # whether an answer exists.
        confidence = min(
            0.95,
            0.55 + (best_score * 0.15)
        )

        return {
            "category": best_category,
            "confidence": round(
                confidence,
                2
            ),
            "reason": (
                f"Matched {best_score} "
                f"keyword(s) associated with "
                f"{best_category}."
            ),
            "scores": scores
        }
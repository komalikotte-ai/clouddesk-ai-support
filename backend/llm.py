import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


# Deterministic marker the LLM must return verbatim when the
# knowledge base doesn't cover the question. Checking for this
# exact token is reliable; checking for free-text phrases like
# "cannot answer" is not, because the model rarely reproduces
# hardcoded wording exactly and a missed match silently gets
# treated as a confident, grounded answer.
NOT_FOUND_TOKEN = "NOT_FOUND_IN_KB"


class LLMService:

    def __init__(self):

        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = "gemini-3.6-flash"

    # ================================================================
    # GENERATE SUPPORT ANSWER
    # ================================================================

    def generate_answer(
        self,
        question,
        context
    ):

        prompt = f"""
You are the Tier-1 Customer Support AI Employee
for a fictional SaaS product called CloudDesk.

Your job is to answer the customer's question
using ONLY the provided CloudDesk knowledge base.

STRICT RULES:

1. Do not invent information.
2. Do not assume missing procedures.
3. Do not create policies that are not present.
4. Do not invent prices, features, URLs, or support procedures.
5. If the knowledge base does not contain enough information
   to answer the question, respond with EXACTLY this token
   and nothing else, no punctuation, no explanation:

   {NOT_FOUND_TOKEN}

6. Keep answers concise and professional.
7. Use the knowledge base context as the only source of truth.

Customer question:
{question}

CloudDesk knowledge base:
{context}

Answer the customer now.
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        if not response or not response.text:
            return NOT_FOUND_TOKEN

        return response.text.strip()
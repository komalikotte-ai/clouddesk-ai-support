from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.append(
    str(PROJECT_ROOT)
)


from backend.llm import LLMService


llm = LLMService()


question = "Why was I charged twice?"


context = """
Q: Why was I charged twice?

A: Duplicate charges may occur when two payment attempts
are processed for the same billing period. Customers
should first check their billing history. If two completed
charges exist for the same invoice period, the customer
should contact CloudDesk Billing Support for investigation
and refund processing.
"""


answer = llm.generate_answer(
    question,
    context
)


print("\nQUESTION:")
print(question)

print("\nANSWER:")
print(answer)
import re

DISCLAIMER = "_This is not medical advice. Consult a licensed clinician for diagnosis or treatment._"

def add_disclaimer(answer: str) -> str:
    return f"{DISCLAIMER}\n\n{answer}"

def redact_phi(text: str) -> str:
    # Very conservative simple redactions (you can expand later)
    text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]", text)
    text = re.sub(r"\b(\d{10}|\+?\d{1,3}\s?\d{7,12})\b", "[REDACTED_PHONE]", text)
    text = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w{2,}\b", "[REDACTED_EMAIL]", text)
    return text

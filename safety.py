from src.utils.postprocess import redact_phi

def safety_filter(user_text: str) -> str:
    # Redact obvious PHI, reject self-harm, illegal requests (extend as needed)
    cleaned = redact_phi(user_text)
    return cleaned
